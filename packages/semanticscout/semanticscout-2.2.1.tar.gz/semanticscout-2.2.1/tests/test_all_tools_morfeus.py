"""
Comprehensive test of all SemanticScout MCP tools on moRFeus_Qt repository.

Similar to test_all_tools.py (Weather Unified), but for the moRFeus_Qt C# codebase.

Tests:
1. Index codebase (full indexing)
2. Search code (semantic search)
3. Find symbol (symbol lookup)
4. Find callers (call graph)
5. Trace dependencies (dependency analysis)
6. Get indexing status (metadata)
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from semanticscout.embeddings.ollama_provider import OllamaEmbeddingProvider
from semanticscout.vector_store.chroma_store import ChromaVectorStore
from semanticscout.symbol_table.symbol_table import SymbolTable
from semanticscout.dependency_graph.dependency_graph import DependencyGraph
from semanticscout.indexer.pipeline import IndexingPipeline
from semanticscout.retriever.semantic_search import SemanticSearcher
from semanticscout.retriever.query_processor import QueryProcessor

# Configuration
MORFEUS_QT_PATH = Path("C:/git/moRFeus_Qt")
COLLECTION_NAME = "morfeus_qt_test"
PERSIST_DIR = "./data/test_chroma_morfeus"


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print('=' * 80)


def test_index_codebase():
    """Test 1: Index the moRFeus_Qt codebase."""
    print_section("TEST 1: Index moRFeus_Qt Codebase")
    
    if not MORFEUS_QT_PATH.exists():
        print(f"❌ moRFeus_Qt repository not found at {MORFEUS_QT_PATH}")
        print("   Please clone the repository or update the path.")
        return None, None, None, None
    
    print(f"Codebase: {MORFEUS_QT_PATH}")
    print(f"Collection: {COLLECTION_NAME}")
    
    # Create components
    embedding_provider = OllamaEmbeddingProvider()
    vector_store = ChromaVectorStore(persist_directory=PERSIST_DIR)
    symbol_table = SymbolTable(collection_name=COLLECTION_NAME)
    dependency_graph = DependencyGraph()
    
    # Create indexing pipeline
    pipeline = IndexingPipeline(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
        symbol_table=symbol_table,
        dependency_graph=dependency_graph,
    )
    
    # Index codebase
    print("\n⏳ Indexing codebase (this may take a few minutes)...")
    start_time = time.time()

    result = pipeline.index_codebase(
        root_path=str(MORFEUS_QT_PATH),
        collection_name=COLLECTION_NAME,
    )

    elapsed = time.time() - start_time

    print(f"\n✅ Indexing complete in {elapsed:.2f}s")
    print(f"   Files indexed: {result.files_indexed}")
    print(f"   Chunks created: {result.chunks_created}")
    print(f"   Symbols extracted: {result.symbols_extracted}")
    print(f"   Dependencies tracked: {result.dependencies_tracked}")
    
    return embedding_provider, vector_store, symbol_table, dependency_graph


def test_search_code(vector_store, embedding_provider):
    """Test 2: Semantic code search."""
    print_section("TEST 2: Semantic Code Search")
    
    if not vector_store or not embedding_provider:
        print("⏭️  Skipping (indexing failed)")
        return
    
    # Create semantic search
    query_processor = QueryProcessor(embedding_provider=embedding_provider)
    search = SemanticSearcher(
        vector_store=vector_store,
        query_processor=query_processor,
    )
    
    # Test queries
    queries = [
        "USB device communication",
        "frequency control",
        "GUI initialization",
        "error handling",
        "serial port communication",
    ]
    
    print("\n🔎 Running search queries...")
    for query in queries:
        results = search.search(
            query=query,
            collection_name=COLLECTION_NAME,
            top_k=3,
        )
        
        print(f"\n  Query: '{query}'")
        print(f"  Results: {len(results)}")

        for i, result in enumerate(results[:2], 1):  # Show top 2
            print(f"    {i}. {result.file_path} "
                  f"(score: {result.similarity_score:.3f})")
            # Show snippet
            snippet = result.content[:100].replace('\n', ' ')
            print(f"       {snippet}...")


def test_find_symbol(symbol_table):
    """Test 3: Symbol lookup."""
    print_section("TEST 3: Symbol Lookup")
    
    if not symbol_table:
        print("⏭️  Skipping (indexing failed)")
        return
    
    # Test symbol searches
    symbols = ["Form", "MainForm", "Device", "USB", "Port"]
    
    print("\n📚 Searching for symbols...")
    for symbol_name in symbols:
        results = symbol_table.search_symbols(
            query=symbol_name,
            limit=3,
        )
        
        print(f"\n  Symbol: '{symbol_name}'")
        print(f"  Found: {len(results)} matches")
        
        for result in results[:2]:  # Show top 2
            print(f"    - {result.get('name', 'unknown')} "
                  f"({result.get('type', 'unknown')}) "
                  f"in {result.get('file_path', 'unknown')}")


def test_find_callers(symbol_table):
    """Test 4: Find callers (call graph)."""
    print_section("TEST 4: Find Callers")
    
    if not symbol_table:
        print("⏭️  Skipping (indexing failed)")
        return
    
    # First, find a common symbol
    results = symbol_table.search_symbols(query="Main", limit=5)
    
    if not results:
        print("⏭️  No symbols found to test callers")
        return
    
    print("\n🔗 Finding callers for symbols...")
    for result in results[:2]:  # Test first 2 symbols
        symbol_name = result.get('name', '')
        print(f"\n  Symbol: {symbol_name}")
        
        # Note: find_callers would require call graph analysis
        # For now, just show that we found the symbol
        print(f"    Type: {result.get('type', 'unknown')}")
        print(f"    File: {result.get('file_path', 'unknown')}")
        print(f"    Line: {result.get('line_number', 'unknown')}")


def test_trace_dependencies(dependency_graph):
    """Test 5: Trace file dependencies."""
    print_section("TEST 5: Trace Dependencies")
    
    if not dependency_graph:
        print("⏭️  Skipping (indexing failed)")
        return
    
    # Get dependency graph stats
    stats = dependency_graph.get_statistics()
    
    print("\n🕸️  Dependency Graph Statistics:")
    print(f"   Total nodes: {stats.get('total_nodes', 0)}")
    print(f"   Total edges: {stats.get('total_edges', 0)}")
    print(f"   File nodes: {stats.get('file_nodes', 0)}")
    print(f"   Symbol nodes: {stats.get('symbol_nodes', 0)}")
    print(f"   File dependencies: {stats.get('file_dependencies', 0)}")
    print(f"   Symbol dependencies: {stats.get('symbol_dependencies', 0)}")
    
    # Try to get dependencies for a file
    if stats.get('file_nodes', 0) > 0:
        # Get all files from graph
        all_files = list(dependency_graph.file_nodes)
        if all_files:
            test_file = all_files[0]
            print(f"\n   Sample file: {test_file}")

            deps = dependency_graph.find_file_dependencies(test_file)
            print(f"   Dependencies: {len(deps)}")
            for dep in deps[:3]:  # Show first 3
                print(f"     - {dep.get('file', 'unknown')} ({dep.get('import_type', 'unknown')})")
                if dep.get('imported_symbols'):
                    print(f"       Symbols: {', '.join(dep['imported_symbols'][:3])}")


def test_get_indexing_status(vector_store, symbol_table):
    """Test 6: Get indexing status and metadata."""
    print_section("TEST 6: Indexing Status")
    
    if not vector_store or not symbol_table:
        print("⏭️  Skipping (indexing failed)")
        return
    
    print("\n📊 Collection Status:")
    
    # Vector store stats
    try:
        collection = vector_store.client.get_collection(name=COLLECTION_NAME)
        count = collection.count()
        print(f"   Vector store chunks: {count}")
    except Exception as e:
        print(f"   Vector store: Error - {e}")
    
    # Symbol table stats
    try:
        cursor = symbol_table.conn.execute(
            "SELECT COUNT(*) FROM symbols WHERE collection_name = ?",
            (COLLECTION_NAME,)
        )
        symbol_count = cursor.fetchone()[0]
        print(f"   Symbol table entries: {symbol_count}")
    except Exception as e:
        print(f"   Symbol table: Error - {e}")
    
    # File metadata
    try:
        cursor = symbol_table.conn.execute(
            "SELECT COUNT(*) FROM file_metadata WHERE collection_name = ?",
            (COLLECTION_NAME,)
        )
        file_count = cursor.fetchone()[0]
        print(f"   Indexed files: {file_count}")
    except Exception as e:
        print(f"   File metadata: Error - {e}")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("  SemanticScout MCP Tools - moRFeus_Qt Comprehensive Test")
    print("=" * 80)
    
    # Test 1: Index codebase
    embedding_provider, vector_store, symbol_table, dependency_graph = test_index_codebase()
    
    if not vector_store:
        print("\n❌ Indexing failed - cannot continue with other tests")
        return
    
    # Test 2: Search code
    test_search_code(vector_store, embedding_provider)
    
    # Test 3: Find symbol
    test_find_symbol(symbol_table)
    
    # Test 4: Find callers
    test_find_callers(symbol_table)
    
    # Test 5: Trace dependencies
    test_trace_dependencies(dependency_graph)
    
    # Test 6: Get indexing status
    test_get_indexing_status(vector_store, symbol_table)
    
    print("\n" + "=" * 80)
    print("  ✅ All tests complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

