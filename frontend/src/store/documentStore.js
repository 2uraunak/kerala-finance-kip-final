import { create } from 'zustand'

export const useDocumentStore = create((set, get) => ({
  documents: [],
  selectedDocument: null,
  searchResults: [],
  isLoading: false,
  error: null,

  setDocuments: (docs) => set({ documents: docs }),
  setSelectedDocument: (doc) => set({ selectedDocument: doc }),
  setSearchResults: (results) => set({ searchResults: results }),
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error }),
  
  clearSearch: () => set({ searchResults: [], error: null })
}))
