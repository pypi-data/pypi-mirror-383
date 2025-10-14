"""
Main CLI interface for Maekrak log analyzer.
"""

import click
from typing import Optional
import json

from maekrak import __version__
from maekrak.core.maekrak_engine import MaekrakEngine


@click.group()
@click.option('--config', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.version_option(version=__version__)
@click.pass_context
def maekrak(ctx: click.Context, config: Optional[str], verbose: bool) -> None:
    """Maekrak - AI-powered log analyzer for local environments.
    
    Analyze log files using natural language queries and AI-powered semantic search.
    All processing happens locally without external dependencies.
    """
    # Ensure that ctx.obj exists and is a dict
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose
    
    # Initialize engine
    engine_config = {}
    if config:
        # TODO: Load config from file
        pass
    
    ctx.obj['engine'] = MaekrakEngine(engine_config)
    
    if verbose:
        click.echo(f"Maekrak v{__version__} - Verbose mode enabled")


@maekrak.command()
@click.option('--offline', is_flag=True, help='Use offline mode (cached models only)')
@click.option('--force', is_flag=True, help='Force re-download models')
@click.pass_context
def init(ctx: click.Context, offline: bool, force: bool) -> None:
    """Initialize Maekrak for first-time use."""
    engine: MaekrakEngine = ctx.obj['engine']
    verbose = ctx.obj.get('verbose', False)
    
    try:
        click.echo("🚀 Initializing Maekrak...")
        click.echo()
        
        # Initialize AI models with progress feedback
        with click.progressbar(length=100, label='Setting up AI models') as bar:
            bar.update(10)  # Starting initialization
            
            result = engine.initialize_ai_models(
                offline_mode=offline, 
                force_download=force,
                progress_callback=lambda progress: bar.update(progress - bar.pos)
            )
            
            bar.update(100 - bar.pos)  # Complete the progress bar
        
        if result['success']:
            model_info = result.get('model_info', {})
            click.echo(f"✓ AI model ready: {result['model_name']}")
            click.echo(f"  Description: {model_info.get('description', 'N/A')}")
            click.echo(f"  Languages: {', '.join(model_info.get('languages', []))}")
            click.echo(f"  Size: {model_info.get('size_mb', 0)} MB")
            click.echo()
        else:
            click.echo(f"✗ AI model initialization failed: {result.get('error', 'Unknown error')}", err=True)
            return
        
        # Check system status
        click.echo("Checking system status...")
        stats = engine.get_statistics()
        
        if stats['success']:
            click.echo("✓ Database ready")
            click.echo("✓ Search index ready")
            click.echo()
            click.echo("Maekrak is ready to use!")
            click.echo()
            click.echo("Next steps:")
            click.echo("  1. Load log files: maekrak load /path/to/logs")
            click.echo("  2. Search logs: maekrak search 'your query'")
            click.echo("  3. View status: maekrak status")
        else:
            click.echo(f"✗ System check failed: {stats.get('error', 'Unknown error')}", err=True)
            
    except Exception as e:
        click.echo(f"Error during initialization: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


@maekrak.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show system status and statistics."""
    engine: MaekrakEngine = ctx.obj['engine']
    verbose = ctx.obj.get('verbose', False)
    
    try:
        click.echo("🔍 Checking system status...")
        
        stats = engine.get_statistics()
        
        if stats['success']:
            click.echo("✅ System status check completed")
            click.echo()
            click.echo("=== Maekrak System Status ===")
            click.echo()
            
            # Database statistics
            db_stats = stats['database']
            click.echo("📊 Database:")
            click.echo(f"  Log entries: {db_stats.get('log_entries_count', 0):,}")
            click.echo(f"  Clusters: {db_stats.get('clusters_count', 0):,}")
            click.echo(f"  Anomalies: {db_stats.get('anomalies_count', 0):,}")
            click.echo(f"  Files processed: {db_stats.get('files_count', 0):,}")
            click.echo()
            
            # Search index statistics
            search_stats = stats['search_index']
            click.echo("🔎 Search Index:")
            click.echo(f"  Indexed entries: {search_stats.get('indexed_count', 0):,}")
            click.echo(f"  Index size: {search_stats.get('index_size_mb', 0):.1f} MB")
            click.echo()
            
            # File processor statistics
            file_stats = stats['file_processor']
            click.echo("📁 File Processor:")
            click.echo(f"  Loaded files: {file_stats.get('loaded_files', 0):,}")
            
            # Show processing performance if available
            if file_stats.get('last_processing_rate'):
                click.echo(f"  Last processing rate: {file_stats['last_processing_rate']:,.0f} entries/s")
            click.echo()
            
            # AI model status
            model_status = engine.model_initializer.get_system_status()
            click.echo("🧠 AI Models:")
            
            if model_status['sentence_transformers_available']:
                click.echo("  Sentence Transformers: ✅ Available")
            else:
                click.echo("  Sentence Transformers: ❌ Not Available")
            
            cache_info = model_status['cache_info']
            click.echo(f"  Cached models: {cache_info['model_count']}")
            click.echo(f"  Cache size: {cache_info['total_size_mb']:.1f} MB")
            
            # Show model details if verbose
            if verbose and cache_info['models']:
                click.echo("  Available models:")
                for model in cache_info['models']:
                    click.echo(f"    - {model}")
            click.echo()
            
            # Migration status
            current_version = engine.migration_manager.get_current_version()
            latest_version = engine.migration_manager.get_latest_version()
            
            click.echo("🗄️  Database Schema:")
            click.echo(f"  Current version: {current_version}")
            click.echo(f"  Latest version: {latest_version}")
            if current_version < latest_version:
                click.echo("  ⚠️  Migration needed - run 'maekrak init' to update")
            else:
                click.echo("  ✅ Up to date")
            click.echo()
            
            # System resources
            click.echo("💾 System:")
            click.echo(f"  Data directory: {stats['data_directory']}")
            
            # Show disk usage if available
            if stats.get('disk_usage'):
                disk_usage = stats['disk_usage']
                click.echo(f"  Disk usage: {disk_usage['used_mb']:.1f} MB")
                if disk_usage.get('available_mb'):
                    click.echo(f"  Available space: {disk_usage['available_mb']:.1f} MB")
        else:
            click.echo(f"❌ Error getting system status: {stats.get('error', 'Unknown error')}", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()


@maekrak.command()
@click.argument('paths', nargs=-1, required=True)
@click.option('--recursive', '-r', is_flag=True, help='Recursively load log files')
@click.pass_context
def load(ctx: click.Context, paths: tuple, recursive: bool) -> None:
    """Load log files for analysis.
    
    PATHS: One or more file paths or directories to load log files from.
    """
    verbose = ctx.obj.get('verbose', False)
    engine = ctx.obj['engine']
    
    if verbose:
        click.echo(f"📁 Loading files: {', '.join(paths)}")
        click.echo(f"🔄 Recursive: {recursive}")
    
    try:
        # Show initial progress
        click.echo("🔍 Scanning for log files...")
        
        # Load files using engine with progress callback
        def progress_callback(stage: str, current: int, total: int, message: str = ""):
            if stage == "scanning":
                click.echo(f"   Found {current} log files...")
            elif stage == "loading":
                if total > 0:
                    percentage = (current / total) * 100
                    click.echo(f"   Processing: {current}/{total} files ({percentage:.1f}%) - {message}")
            elif stage == "parsing":
                if total > 0:
                    percentage = (current / total) * 100
                    click.echo(f"   Parsing: {current:,}/{total:,} lines ({percentage:.1f}%)")
        
        result = engine.load_files(
            list(paths), 
            recursive, 
            progress_callback=progress_callback
        )
        
        if result['success']:
            click.echo()
            click.echo(f"✅ Successfully loaded {result['files_loaded']} files")
            click.echo(f"📊 Processed {result['log_entries_processed']:,} log entries")
            click.echo(f"⏱️  Processing time: {result['processing_time']:.2f}s")
            
            # Show processing rate
            if result['processing_time'] > 0:
                rate = result['log_entries_processed'] / result['processing_time']
                click.echo(f"🚀 Processing rate: {rate:,.0f} entries/second")
            
            if verbose and result.get('errors'):
                click.echo("⚠️  Warnings:")
                for error in result['errors']:
                    click.echo(f"   {error}")
        else:
            click.echo("❌ Failed to load files:")
            for error in result.get('errors', []):
                click.echo(f"   {error}")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()


@maekrak.command()
@click.argument('query')
@click.option('--limit', '-l', default=10, help='Number of results to show')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['table', 'json', 'raw']), 
              default='table', help='Output format')
@click.option('--time-range', help='Time range filter (e.g., "1h", "24h", "7d")')
@click.option('--service', multiple=True, help='Filter by service name')
@click.option('--level', multiple=True, help='Filter by log level')
@click.pass_context
def search(ctx: click.Context, query: str, limit: int, output_format: str, 
          time_range: Optional[str], service: tuple, level: tuple) -> None:
    """Search logs using natural language queries.
    
    QUERY: Natural language query to search for in logs.
    """
    verbose = ctx.obj.get('verbose', False)
    engine = ctx.obj['engine']
    
    if verbose:
        click.echo(f"🔍 Searching for: '{query}'")
        click.echo(f"📊 Limit: {limit}, Format: {output_format}")
        if time_range:
            click.echo(f"⏰ Time range: {time_range}")
    
    try:
        # Show search progress
        click.echo(f"🔍 Searching for: '{query}'")
        
        def search_progress_callback(stage: str, progress: int, message: str = ""):
            if stage == "embedding":
                click.echo(f"   🧠 Generating query embedding... ({progress}%)")
            elif stage == "searching":
                click.echo(f"   🔎 Searching vector index... ({progress}%)")
            elif stage == "filtering":
                click.echo(f"   🔧 Applying filters... ({progress}%)")
            elif stage == "ranking":
                click.echo(f"   📊 Ranking results... ({progress}%)")
        
        # Perform search
        result = engine.search(
            query=query,
            limit=limit,
            time_range=time_range,
            services=list(service) if service else None,
            levels=list(level) if level else None,
            progress_callback=search_progress_callback
        )
        
        if result['success']:
            search_time = result.get('search_time', 0)
            total_candidates = result.get('total_candidates', 0)
            
            click.echo(f"   ✅ Search completed in {search_time:.2f}s")
            if total_candidates > 0:
                click.echo(f"   📈 Searched {total_candidates:,} log entries")
            click.echo()
            
            if output_format == 'json':
                click.echo(json.dumps(result, indent=2, default=str))
            else:
                _display_search_results(result, output_format, verbose)
        else:
            click.echo(f"❌ Search failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()


@maekrak.command()
@click.option('--clusters', is_flag=True, help='Show log clusters')
@click.option('--anomalies', is_flag=True, help='Show anomaly detection results')
@click.pass_context
def analyze(ctx: click.Context, clusters: bool, anomalies: bool) -> None:
    """Analyze logs for patterns and anomalies."""
    verbose = ctx.obj.get('verbose', False)
    engine = ctx.obj['engine']
    
    if verbose:
        click.echo(f"🔬 Analysis requested - Clusters: {clusters}, Anomalies: {anomalies}")
    
    try:
        if not clusters and not anomalies:
            # Default to both if none specified
            clusters = anomalies = True
        
        click.echo("🔬 Starting log analysis...")
        
        def analysis_progress_callback(stage: str, progress: int, message: str = ""):
            if stage == "clustering":
                click.echo(f"   🎯 Clustering log patterns... ({progress}%)")
            elif stage == "anomaly_detection":
                click.echo(f"   🚨 Detecting anomalies... ({progress}%)")
            elif stage == "generating_embeddings":
                click.echo(f"   🧠 Generating embeddings... ({progress}%)")
            elif stage == "building_clusters":
                click.echo(f"   🔗 Building clusters... ({progress}%)")
        
        results = {}
        
        if clusters:
            click.echo("   🎯 Performing cluster analysis...")
            cluster_result = engine.analyze_clusters(progress_callback=analysis_progress_callback)
            results['clusters'] = cluster_result
        
        if anomalies:
            click.echo("   🚨 Performing anomaly detection...")
            anomaly_result = engine.detect_anomalies(progress_callback=analysis_progress_callback)
            results['anomalies'] = anomaly_result
        
        # Display results
        click.echo("   ✅ Analysis completed")
        click.echo()
        
        if clusters and results.get('clusters', {}).get('success'):
            cluster_data = results['clusters']
            click.echo("📊 Cluster Analysis Results:")
            click.echo(f"   Found {len(cluster_data.get('clusters', []))} distinct patterns")
            click.echo(f"   Analysis time: {cluster_data.get('analysis_time', 0):.2f}s")
            click.echo()
        
        if anomalies and results.get('anomalies', {}).get('success'):
            anomaly_data = results['anomalies']
            click.echo("🚨 Anomaly Detection Results:")
            click.echo(f"   Found {len(anomaly_data.get('anomalies', []))} anomalies")
            click.echo(f"   Analysis time: {anomaly_data.get('analysis_time', 0):.2f}s")
            click.echo()
        
        # Show any errors
        for analysis_type, result in results.items():
            if not result.get('success'):
                click.echo(f"❌ {analysis_type.title()} analysis failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()


@maekrak.command()
@click.argument('trace_id')
@click.option('--format', '-f', 'output_format', 
              type=click.Choice(['table', 'json', 'timeline']), 
              default='timeline', help='Output format')
@click.pass_context
def trace(ctx: click.Context, trace_id: str, output_format: str) -> None:
    """Trace distributed requests by trace ID.
    
    TRACE_ID: The trace ID to search for across all loaded logs.
    """
    verbose = ctx.obj.get('verbose', False)
    engine = ctx.obj['engine']
    
    if verbose:
        click.echo(f"🔍 Tracing ID: {trace_id}")
    
    try:
        # Show trace progress
        click.echo(f"🔍 Analyzing trace: {trace_id}")
        
        def trace_progress_callback(stage: str, progress: int, message: str = ""):
            if stage == "searching":
                click.echo(f"   🔎 Searching for trace entries... ({progress}%)")
            elif stage == "analyzing":
                click.echo(f"   🔬 Analyzing request flow... ({progress}%)")
            elif stage == "building_timeline":
                click.echo(f"   📅 Building timeline... ({progress}%)")
        
        # Analyze trace
        result = engine.trace(trace_id, progress_callback=trace_progress_callback)
        
        if result['success']:
            analysis_time = result.get('analysis_time', 0)
            entries_found = result.get('entries_found', 0)
            
            click.echo(f"   ✅ Trace analysis completed in {analysis_time:.2f}s")
            click.echo(f"   📊 Found {entries_found} related log entries")
            click.echo()
            
            if output_format == 'json':
                click.echo(json.dumps(result, indent=2, default=str))
            else:
                _display_trace_results(result, output_format, verbose)
        else:
            click.echo(f"❌ Trace analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}")
        if verbose:
            import traceback
            traceback.print_exc()


def _display_search_results(result: dict, output_format: str, verbose: bool) -> None:
    """Display search results in the specified format."""
    results = result.get('results', [])
    
    if not results:
        click.echo("No results found.")
        return
    
    click.echo(f"Found {len(results)} results:")
    click.echo()
    
    for i, search_result in enumerate(results, 1):
        log_entry = search_result['log_entry']
        similarity = search_result['similarity']
        
        if output_format == 'table':
            click.echo(f"{i}. [{log_entry['level']}] {log_entry['service']} - {similarity:.2%}")
            click.echo(f"   {log_entry['timestamp']}")
            click.echo(f"   {log_entry['message']}")
            if verbose and log_entry.get('trace_id'):
                click.echo(f"   Trace ID: {log_entry['trace_id']}")
            click.echo()
        elif output_format == 'raw':
            click.echo(f"{similarity:.2%} | {log_entry['raw_line']}")


def _display_trace_results(result: dict, output_format: str, verbose: bool) -> None:
    """Display trace analysis results."""
    trace_flow = result.get('trace_flow', {})
    timeline = result.get('timeline', [])
    anomalies = result.get('anomalies', [])
    
    click.echo(f"Trace Analysis: {result['trace_id']}")
    click.echo(f"Services: {', '.join(trace_flow.get('services', []))}")
    click.echo(f"Duration: {trace_flow.get('total_duration_seconds', 0):.2f}s")
    click.echo(f"Log entries: {trace_flow.get('total_log_count', 0)}")
    
    if trace_flow.get('error_count', 0) > 0:
        click.echo(f"❌ Errors: {trace_flow['error_count']}")
    
    if trace_flow.get('warning_count', 0) > 0:
        click.echo(f"⚠️  Warnings: {trace_flow['warning_count']}")
    
    if anomalies:
        click.echo("\n🔍 Anomalies detected:")
        for anomaly in anomalies:
            click.echo(f"   - {anomaly['type']}: {anomaly['description']}")
    
    if output_format == 'timeline' and timeline:
        click.echo("\n📅 Timeline:")
        for event in timeline[:20]:  # Limit to first 20 events
            timestamp = event['timestamp']
            service = event['service']
            level = event['level']
            message = event['message'][:80] + "..." if len(event['message']) > 80 else event['message']
            
            icon = "❌" if event.get('is_error') else "⚠️" if event.get('is_warning') else "ℹ️"
            click.echo(f"   {timestamp} | {icon} {service} [{level}] {message}")


def main() -> None:
    """Entry point for the CLI application."""
    maekrak()


if __name__ == '__main__':
    main()