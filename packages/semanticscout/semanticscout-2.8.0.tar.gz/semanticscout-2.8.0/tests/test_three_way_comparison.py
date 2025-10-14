"""
Three-Way Comparison Test: All Paths with Query Testing

Tests all three indexing paths:
1. Tree-sitter + Ollama
2. Tree-sitter + Sentence-Transformers
3. LSP (jedi) + Sentence-Transformers

For each path, tests:
- Indexing performance
- Symbol extraction count
- Dependency tracking count
- Language detection accuracy
- Dependency analysis effectiveness
- Search quality with actual queries
"""

import json
import os
import shutil
import sys
import time
from pathlib import Path

# Test configuration
MORFEUS_QT_PATH = "C:/git/moRFeus_Qt"
TEST_DATA_DIR = Path("C:/git/Indexer101/.semanticscout-three-way-comparison")

# Test queries
TEST_QUERIES = [
    "USB HID device communication",
    "frequency generator control",
    "Qt GUI main window"
]

print("="*80)
print("THREE-WAY COMPARISON TEST - ALL PATHS WITH QUERIES")
print("="*80)
print()
print("Test repository:", MORFEUS_QT_PATH)
print("Test queries:", len(TEST_QUERIES))
for i, q in enumerate(TEST_QUERIES, 1):
    print(f"  {i}. {q}")
print()

# Clean up
if TEST_DATA_DIR.exists():
    print(f"Cleaning up: {TEST_DATA_DIR}")
    shutil.rmtree(TEST_DATA_DIR)
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)

results = {}

def run_test(test_name, config, data_dir, collection_suffix=""):
    """Run a single test configuration"""
    print("="*80)
    print(f"TEST: {test_name}")
    print("="*80)
    print()

    # Set config and data directory
    os.environ["SEMANTICSCOUT_CONFIG_JSON"] = json.dumps(config)
    os.environ["SEMANTICSCOUT_DATA_DIR"] = str(data_dir)

    # Reload modules
    for module in list(sys.modules.keys()):
        if module.startswith('semanticscout'):
            del sys.modules[module]

    # Import
    from semanticscout import mcp_server
    from semanticscout.mcp_server import (
        index_codebase,
        search_code,
        find_symbol,
        list_collections,
        initialize_components,
    )

    # Initialize
    print("Initializing components...")
    initialize_components()
    print("[OK] Initialized")
    print()

    # Get managers from the module after initialization
    symbol_table_manager = mcp_server.symbol_table_manager
    dependency_graph_manager = mcp_server.dependency_graph_manager

    # Test language detection first
    print("Testing language detection...")
    language_detection_result = None
    try:
        from semanticscout.language_detection.project_language_detector import ProjectLanguageDetector
        from pathlib import Path
        detector = ProjectLanguageDetector()
        language_detection_result = detector.detect_languages(Path(MORFEUS_QT_PATH))
        print(f"  Primary language: {language_detection_result.primary_language}")
        print(f"  Languages detected: {list(language_detection_result.languages.keys())}")
        print(f"  Detection confidence: {language_detection_result.confidence:.2f}")
    except Exception as e:
        print(f"  Warning: Language detection failed: {e}")
    print()

    # Index - the collection name is auto-generated from the path + embedding provider
    # For moRFeus_Qt with different providers, it will be:
    # - "morfeus_qt_nomic_embed_text" (Ollama)
    # - "morfeus_qt_all_minilm_l6_v2" (Sentence-Transformers)
    print(f"Indexing moRFeus_Qt...")
    start_time = time.time()
    index_result = index_codebase(path=MORFEUS_QT_PATH, incremental=False)
    index_time = time.time() - start_time

    # Verify collection was created using list_collections (NEW response format)
    print("  Verifying collection creation...")
    collections_result = list_collections()

    # Find our collection in the response
    collection_found = False
    actual_collection_name = None
    expected_model = config["embedding"]["model"]

    for coll in collections_result.get("collections", []):
        # Match by name prefix (morfeus_qt_) and embedding model
        if coll["name"].startswith("morfeus_qt_") and coll["embedding_model"] == expected_model:
            collection_found = True
            actual_collection_name = coll["name"]  # Use the full UUID-based name
            print(f"  ✓ Collection found in list_collections:")
            print(f"    - Name: {coll['name']}")
            print(f"    - Model: {coll['embedding_model']}")
            print(f"    - Dimensions: {coll.get('embedding_dimensions', 'unknown')}")
            print(f"    - Processor: {coll.get('processor_type', 'unknown')}")
            print(f"    - Chunks: {coll['chunk_count']}")
            break

    if not collection_found:
        print(f"  ✗ ERROR: Collection not found in list_collections")
        print(f"  Available collections:")
        for coll in collections_result.get("collections", []):
            print(f"    - {coll['name']} ({coll['embedding_model']})")
        raise Exception("Collection not found after indexing")

    print(f"  Using collection name for operations: {actual_collection_name}")

    # Get stats - handle case where managers might be None
    symbols_count = 0
    dependencies_count = 0
    dependency_analysis_stats = {}

    if symbol_table_manager is not None:
        try:
            symbol_table = symbol_table_manager.get_table(actual_collection_name)
            stats = symbol_table.get_statistics()
            symbols_count = stats['total_symbols']
        except Exception as e:
            print(f"Warning: Could not get symbol statistics: {e}")
            symbols_count = 0
    else:
        print("Warning: symbol_table_manager is None - enhancement features may be disabled")

    if dependency_graph_manager is not None:
        try:
            dependency_graph = dependency_graph_manager.get_graph(actual_collection_name)
            dependencies_count = dependency_graph.graph.number_of_edges()

            # Get dependency analysis statistics
            try:
                # Count different types of dependencies
                import_deps = 0
                call_deps = 0
                inheritance_deps = 0

                for _, _, data in dependency_graph.graph.edges(data=True):
                    dep_type = data.get('type', 'unknown')
                    if dep_type == 'import':
                        import_deps += 1
                    elif dep_type == 'call':
                        call_deps += 1
                    elif dep_type == 'inheritance':
                        inheritance_deps += 1

                dependency_analysis_stats = {
                    'import_dependencies': import_deps,
                    'call_dependencies': call_deps,
                    'inheritance_dependencies': inheritance_deps,
                    'total_nodes': dependency_graph.graph.number_of_nodes()
                }
            except Exception as e:
                print(f"Warning: Could not analyze dependency types: {e}")

        except Exception as e:
            print(f"Warning: Could not get dependency statistics: {e}")
            dependencies_count = 0
    else:
        print("Warning: dependency_graph_manager is None - enhancement features may be disabled")

    print(f"[OK] Indexed in {index_time:.2f}s")
    print(f"  Symbols: {symbols_count}")
    print(f"  Dependencies: {dependencies_count}")
    if dependency_analysis_stats:
        print(f"  Import deps: {dependency_analysis_stats.get('import_dependencies', 0)}")
        print(f"  Call deps: {dependency_analysis_stats.get('call_dependencies', 0)}")
        print(f"  Inheritance deps: {dependency_analysis_stats.get('inheritance_dependencies', 0)}")
        print(f"  Total nodes: {dependency_analysis_stats.get('total_nodes', 0)}")
    print()
    
    # Test queries
    query_results = []
    for i, query in enumerate(TEST_QUERIES, 1):
        print(f"Query {i}/{len(TEST_QUERIES)}: {query}")
        start_time = time.time()
        search_result = search_code(
            query=query,
            collection_name=actual_collection_name,
            top_k=3,
            expansion_level="medium"
        )
        query_time = time.time() - start_time

        query_results.append({
            'query': query,
            'result_length': len(search_result),
            'query_time': query_time
        })
        print(f"  Result: {len(search_result)} chars in {query_time:.3f}s")

    print()

    # Test symbol lookup
    print("Symbol lookup: MoRFeus class")
    symbol_result = find_symbol(symbol_name="MoRFeus", collection_name=actual_collection_name, symbol_type="class")
    symbol_found = "MoRFeus" in symbol_result
    print(f"  Found: {symbol_found}")
    print()
    
    return {
        'name': test_name,
        'index_time': index_time,
        'symbols': symbols_count,
        'dependencies': dependencies_count,
        'dependency_analysis': dependency_analysis_stats,
        'language_detection': language_detection_result,
        'symbol_found': symbol_found,
        'queries': query_results
    }

# ============================================================================
# TEST 1: Tree-sitter + Ollama
# ============================================================================
test1_dir = TEST_DATA_DIR / "test1_treesitter_ollama"
test1_dir.mkdir(parents=True, exist_ok=True)

results['test1'] = run_test(
    "Tree-sitter + Ollama",
    {
        "embedding": {"provider": "ollama", "model": "nomic-embed-text"},
        "lsp_integration": {"enabled": False},
        "features": {
            "enable_ast_processing": True,
            "enable_symbol_table": True,
            "enable_dependency_graph": True,
            "enable_language_detection": True,
            "enable_dependency_analysis": True
        },
        "language_detection": {
            "enabled": True,
            "confidence_threshold": 0.1
        },
        "dependency_analysis": {
            "enabled": True,
            "strategies": ["rust", "python", "c_sharp", "javascript"]
        }
    },
    test1_dir,
    "_test1"
)

# ============================================================================
# TEST 2: Tree-sitter + Sentence-Transformers
# ============================================================================
test2_dir = TEST_DATA_DIR / "test2_treesitter_st"
test2_dir.mkdir(parents=True, exist_ok=True)

results['test2'] = run_test(
    "Tree-sitter + Sentence-Transformers",
    {
        "embedding": {"provider": "sentence-transformers", "model": "all-MiniLM-L6-v2"},
        "lsp_integration": {"enabled": False},
        "features": {
            "enable_ast_processing": True,
            "enable_symbol_table": True,
            "enable_dependency_graph": True,
            "enable_language_detection": True,
            "enable_dependency_analysis": True
        },
        "language_detection": {
            "enabled": True,
            "confidence_threshold": 0.1
        },
        "dependency_analysis": {
            "enabled": True,
            "strategies": ["rust", "python", "c_sharp", "javascript"]
        }
    },
    test2_dir,
    "_test2"
)

# ============================================================================
# TEST 3: LSP (jedi) + Sentence-Transformers
# ============================================================================
test3_dir = TEST_DATA_DIR / "test3_lsp_st"
test3_dir.mkdir(parents=True, exist_ok=True)

results['test3'] = run_test(
    "LSP (jedi) + Sentence-Transformers",
    {
        "embedding": {"provider": "sentence-transformers", "model": "all-MiniLM-L6-v2"},
        "lsp_integration": {
            "enabled": True,
            "fallback_to_tree_sitter": True,
            "languages": {"python": {"enabled": True, "server": "jedi"}}
        },
        "features": {
            "enable_ast_processing": True,
            "enable_symbol_table": True,
            "enable_dependency_graph": True,
            "enable_language_detection": True,
            "enable_dependency_analysis": True
        },
        "language_detection": {
            "enabled": True,
            "confidence_threshold": 0.1
        },
        "dependency_analysis": {
            "enabled": True,
            "strategies": ["rust", "python", "c_sharp", "javascript"]
        }
    },
    test3_dir,
    "_test3"
)

# ============================================================================
# COMPARISON SUMMARY
# ============================================================================
print("="*80)
print("COMPARISON SUMMARY")
print("="*80)
print()

# Language detection comparison
print("LANGUAGE DETECTION:")
print(f"{'Configuration':<40} {'Primary Lang':<15} {'Confidence':<12} {'Languages':<20}")
print("-"*100)
for key in ['test1', 'test2', 'test3']:
    r = results[key]
    lang_result = r.get('language_detection')
    if lang_result:
        primary = lang_result.primary_language or "None"
        confidence = f"{lang_result.confidence:.2f}"
        languages = ", ".join(list(lang_result.languages.keys())[:3])  # Show first 3
    else:
        primary = "N/A"
        confidence = "N/A"
        languages = "N/A"
    print(f"{r['name']:<40} {primary:<15} {confidence:<12} {languages:<20}")
print()

# Indexing comparison
print("INDEXING PERFORMANCE:")
print(f"{'Configuration':<40} {'Time (s)':<12} {'Symbols':<10} {'Deps':<10} {'Nodes':<10}")
print("-"*90)
for key in ['test1', 'test2', 'test3']:
    r = results[key]
    dep_stats = r.get('dependency_analysis', {})
    nodes = dep_stats.get('total_nodes', 0)
    print(f"{r['name']:<40} {r['index_time']:<12.2f} {r['symbols']:<10} {r['dependencies']:<10} {nodes:<10}")
print()

# Dependency analysis comparison
print("DEPENDENCY ANALYSIS:")
print(f"{'Configuration':<40} {'Import':<8} {'Call':<8} {'Inherit':<8} {'Total':<8}")
print("-"*80)
for key in ['test1', 'test2', 'test3']:
    r = results[key]
    dep_stats = r.get('dependency_analysis', {})
    import_deps = dep_stats.get('import_dependencies', 0)
    call_deps = dep_stats.get('call_dependencies', 0)
    inherit_deps = dep_stats.get('inheritance_dependencies', 0)
    total_deps = r['dependencies']
    print(f"{r['name']:<40} {import_deps:<8} {call_deps:<8} {inherit_deps:<8} {total_deps:<8}")
print()

# Query comparison
print("QUERY PERFORMANCE:")
for i, query in enumerate(TEST_QUERIES, 1):
    print(f"\nQuery {i}: {query}")
    print(f"{'Configuration':<40} {'Time (ms)':<12} {'Result Size':<12}")
    print("-"*80)
    for key in ['test1', 'test2', 'test3']:
        r = results[key]
        q = r['queries'][i-1]
        print(f"{r['name']:<40} {q['query_time']*1000:<12.1f} {q['result_length']:<12}")

print()
print("="*80)
print("KEY FINDINGS:")
print("="*80)

# Calculate differences
t1 = results['test1']
t2 = results['test2']
t3 = results['test3']

# Language detection analysis
print(f"\nLanguage Detection:")
for key, test_name in [('test1', 'Ollama'), ('test2', 'Sentence-Transformers'), ('test3', 'LSP')]:
    r = results[key]
    lang_result = r.get('language_detection')
    if lang_result:
        print(f"  {test_name}: {lang_result.primary_language} (confidence: {lang_result.confidence:.2f})")
        if lang_result.languages:
            top_langs = sorted(lang_result.languages.items(), key=lambda x: x[1], reverse=True)[:3]
            lang_str = ", ".join([f"{lang}({score:.2f})" for lang, score in top_langs])
            print(f"    Top languages: {lang_str}")
    else:
        print(f"  {test_name}: Detection failed")

print(f"\nSymbol Extraction:")
print(f"  Tree-sitter: {t2['symbols']} symbols")
if t2['symbols'] > 0:
    symbol_diff = t3['symbols'] - t2['symbols']
    symbol_pct = ((t3['symbols'] / t2['symbols']) - 1) * 100
    print(f"  LSP (jedi):  {t3['symbols']} symbols ({symbol_diff:+d}, {symbol_pct:+.1f}%)")
else:
    print(f"  LSP (jedi):  {t3['symbols']} symbols (N/A - tree-sitter returned 0)")

print(f"\nDependency Tracking:")
print(f"  Tree-sitter: {t2['dependencies']} dependencies")
if t2['dependencies'] > 0:
    dep_diff = t3['dependencies'] - t2['dependencies']
    dep_pct = ((t3['dependencies'] / t2['dependencies']) - 1) * 100
    print(f"  LSP (jedi):  {t3['dependencies']} dependencies ({dep_diff:+d}, {dep_pct:+.1f}%)")
else:
    print(f"  LSP (jedi):  {t3['dependencies']} dependencies (N/A - tree-sitter returned 0)")

# Dependency analysis breakdown
print(f"\nDependency Analysis Effectiveness:")
for key, test_name in [('test2', 'Tree-sitter'), ('test3', 'LSP')]:
    r = results[key]
    dep_stats = r.get('dependency_analysis', {})
    if dep_stats:
        import_deps = dep_stats.get('import_dependencies', 0)
        call_deps = dep_stats.get('call_dependencies', 0)
        inherit_deps = dep_stats.get('inheritance_dependencies', 0)
        total = import_deps + call_deps + inherit_deps
        if total > 0:
            print(f"  {test_name}: {total} analyzed dependencies")
            print(f"    Import: {import_deps} ({import_deps/total*100:.1f}%)")
            print(f"    Call: {call_deps} ({call_deps/total*100:.1f}%)")
            print(f"    Inheritance: {inherit_deps} ({inherit_deps/total*100:.1f}%)")

print(f"\nIndexing Speed:")
print(f"  Ollama:              {t1['index_time']:.2f}s (baseline)")
if t2['index_time'] > 0:
    speed_ratio = t1['index_time'] / t2['index_time']
    lsp_overhead = t3['index_time'] - t2['index_time']
    lsp_overhead_pct = ((t3['index_time'] / t2['index_time']) - 1) * 100
    print(f"  Sentence-Transformers: {t2['index_time']:.2f}s ({speed_ratio:.1f}x faster)")
    print(f"  LSP overhead:        {lsp_overhead:.2f}s ({lsp_overhead_pct:+.1f}%)")
else:
    print(f"  Sentence-Transformers: {t2['index_time']:.2f}s (N/A)")
    print(f"  LSP overhead:        {t3['index_time'] - t2['index_time']:.2f}s (N/A)")

print()
print("[OK] THREE-WAY COMPARISON COMPLETE")

