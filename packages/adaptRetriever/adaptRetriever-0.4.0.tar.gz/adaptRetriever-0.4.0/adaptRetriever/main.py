
import numpy as np
from scipy.stats import ks_2samp
from sklearn.neighbors import NearestNeighbors
from dadapy import Data
from dadapy._utils import utils as ut
from sentence_transformers import SentenceTransformer
from scipy.spatial import distance
import torch
import random


class aRAG:
    """
    Adaptive Retrieval-Augmented Generation class using intrinsic dimensionality
    and dense retrievers for document selection.
    """
    
    def __init__(self, model_name='sentence-transformers/msmarco-MiniLM-L-12-v3', 
                 k_fallback=5, random_seed=0):
        """
        Initialize the aRAG retrieval system.
        
        Parameters:
        -----------
        model_name : str
            Name of the dense retriever model from sentence-transformers
        k_fallback : int
            Number of documents to retrieve in case of error (fallback mechanism)
        random_seed : int
            Random seed for reproducibility
        """
        self.model_name = model_name
        self.k_fallback = k_fallback
        self.random_seed = random_seed
        
        # Set random seeds
        self._set_seed(random_seed)
        
        # Load the dense retriever model
        self.model = SentenceTransformer(model_name)
        self.rng = np.random.default_rng(random_seed)
        
    def _set_seed(self, seed):
        """Set random seeds for reproducibility."""
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    
    def _compute_id_kstar_binomial(self, data, embeddings, initial_id=None, 
                                   Dthr=23.92812698, r='opt', n_iter=10):
        """
        Compute intrinsic dimensionality and k* using binomial estimator.
        
        Parameters:
        -----------
        data : dadapy.Data
            Data object containing embeddings
        embeddings : np.ndarray
            Document embeddings
        initial_id : float, optional
            Initial estimate of intrinsic dimensionality
        Dthr : float
            Distance threshold for k* computation
        r : str or float
            Ratio for neighborhood shells ('opt' for automatic)
        n_iter : int
            Number of iterations
            
        Returns:
        --------
        ids : np.ndarray
            Intrinsic dimensionality estimates per iteration
        kstars : np.ndarray
            k* values for each data point
        """
        if initial_id is None:
            data.compute_id_2NN(algorithm='base')
        else:
            data.compute_distances()
            data.set_id(initial_id)
        
        ids = np.zeros(n_iter)
        kstars = np.zeros((n_iter, data.N), dtype=int)
        
        for i in range(n_iter):
            # Compute k*
            data.compute_kstar(Dthr)
            
            # Set effective ratio
            r_eff = min(0.95, 0.2032**(1./data.intrinsic_dim)) if r == 'opt' else r
            
            # Compute neighborhood shells from k*
            rk = np.array([dd[data.kstar[j]] for j, dd in enumerate(data.distances)])
            rn = rk * r_eff
            n = np.sum([dd < rn[j] for j, dd in enumerate(data.distances)], axis=1)
            
            # Compute ID
            id_val = np.log((n.mean() - 1) / (data.kstar.mean() - 1)) / np.log(r_eff)
            
            # Set new ID
            data.set_id(id_val)
            ids[i] = id_val
            kstars[i] = data.kstar
        
        return ids, kstars[(n_iter - 1), :]
    
    def _find_k_neighbors(self, embeddings, query_index, k, use_cosine=True):
        """
        Find k nearest neighbors of a query embedding.
        
        Parameters:
        -----------
        embeddings : np.ndarray
            All embeddings (query + documents)
        query_index : int
            Index of the query embedding
        k : int
            Number of neighbors to retrieve
        use_cosine : bool
            Whether to use cosine distance (True) or dot product (False)
            
        Returns:
        --------
        list
            Indices of k nearest neighbors
        """
        target_embedding = embeddings[query_index]
        
        if use_cosine:
            # Compute cosine distance
            all_distances = np.array([distance.cosine(target_embedding, emb) 
                                     for emb in embeddings])
            # Sort by ascending order (smaller distance = higher similarity)
            nearest_indices = np.argsort(all_distances)[1:k+1]
        else:
            # Compute dot product similarity
            from sentence_transformers import util
            all_scores = util.dot_score(target_embedding, embeddings)[0].cpu().tolist()
            # Sort by descending order (larger score = higher similarity)
            nearest_indices = np.argsort(all_scores)[::-1][1:k+1]
        
        return nearest_indices.tolist()
    
    def retrieve(self, query, documents, use_cosine=True, Dthr=23.92812698, 
                 r='opt', n_iter=10):
        """
        Retrieve the most relevant documents for a given query using adaptive RAG.
        
        Parameters:
        -----------
        query : str
            The query text
        documents : list of str
            List of document texts
        use_cosine : bool
            Whether to use cosine distance for similarity
        Dthr : float
            Distance threshold for k* computation
        r : str or float
            Ratio for neighborhood shells
        n_iter : int
            Number of iterations for ID estimation
            
        Returns:
        --------
        list of str
            Retrieved documents (most relevant to the query)
        """
        # Encode query and documents
        query_embedding = self.model.encode(query)
        doc_embeddings = self.model.encode(documents)
        
        # If too few documents, return all
        if len(documents) <= self.k_fallback:
            return documents
        
        try:
            # Concatenate query embedding with document embeddings
            all_embeddings = np.concatenate(
                (np.array(query_embedding).reshape(1, -1), doc_embeddings)
            )
            
            # Create Data object for ID computation
            data = Data(all_embeddings)
            
            # Compute intrinsic dimensionality and k*
            ids, kstars = self._compute_id_kstar_binomial(
                data, 
                doc_embeddings, 
                initial_id=None, 
                Dthr=Dthr, 
                r=r, 
                n_iter=n_iter
            )
            
            # Get k* nearest neighbors for the query (index 0)
            k_optimal = kstars[0]
            neighbor_indices = self._find_k_neighbors(
                all_embeddings, 
                0, 
                k_optimal, 
                use_cosine
            )
            
            # Adjust indices (subtract 1 because query is at index 0)
            doc_indices = np.array(neighbor_indices) - 1
            retrieved_docs = np.array(documents)[doc_indices].tolist()
            
            return retrieved_docs
            
        except (ValueError, Exception) as e:
            # Fallback: return top-k documents by simple similarity
            print(f"⚠️ Error in adaptive retrieval: {e}. Using fallback with k={self.k_fallback}")
            neighbor_indices = self._find_k_neighbors(
                np.concatenate((np.array(query_embedding).reshape(1, -1), doc_embeddings)),
                0,
                min(self.k_fallback, len(documents)),
                use_cosine
            )
            doc_indices = np.array(neighbor_indices) - 1
            return np.array(documents)[doc_indices].tolist()


