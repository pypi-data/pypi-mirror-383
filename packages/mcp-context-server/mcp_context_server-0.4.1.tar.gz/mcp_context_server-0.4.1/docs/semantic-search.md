# Semantic Search Guide

## Introduction

Semantic search enables finding context entries based on meaning rather than exact keyword matching. Using 768-dimensional embeddings from Google's EmbeddingGemma model via Ollama, the MCP Context Server can understand semantic similarity between queries and stored context, making it powerful for:

- Finding related work across different threads
- Discovering similar contexts without shared keywords
- Concept-based retrieval from large context collections
- Cross-agent knowledge discovery

This feature is **optional** and requires additional dependencies and setup.

## Prerequisites

Before enabling semantic search, ensure your system meets these requirements:

- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: ~1.1GB (500MB for Ollama + 600MB for EmbeddingGemma model)
- **Python**: 3.12+ (already required by MCP Context Server)
- **SQLite**: 3.35+ minimum, 3.41+ recommended
- **Network**: Internet connection for initial model download
- **GPU**: Optional (NVIDIA, AMD, Apple Silicon supported for faster embedding generation)

## Installation

### Step 1: Install Ollama

Ollama manages the EmbeddingGemma model and provides the embedding generation API.

#### Windows

1. Download the installer from [ollama.com/download](https://ollama.com/download)
2. Run the .exe installer
3. Verify Windows Defender allows port 11434
4. Test installation:
   ```bash
   ollama --version
   curl http://localhost:11434
   ```

#### macOS

1. Download the .dmg from [ollama.com/download/mac](https://ollama.com/download/mac)
2. Drag Ollama to Applications
3. Launch Ollama app
4. Test installation:
   ```bash
   ollama --version
   curl http://localhost:11434
   ```

**Important macOS Note**: The default macOS Python lacks SQLite extension support. You must use Homebrew Python:

```bash
# Install Homebrew Python
brew install python

# Create virtual environment with Homebrew Python
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate
```

#### Linux

```bash
# Auto-detects GPU support
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
curl http://localhost:11434
```

### Step 2: Install Python Dependencies

```bash
# Using uv (recommended)
uv sync --extra semantic-search
```

You can also install the dependencies globally:

```bash
# Using uv (recommended)
uv pip install -U --system ollama numpy sqlite-vec
```

This installs:
- `ollama>=0.4.0` - Python client for Ollama API
- `numpy>=1.24.0` - Vector operations support
- `sqlite-vec>=0.1.6` - SQLite extension for vector storage

### Step 3: Pull the EmbeddingGemma Model

```bash
# Download the model (~622MB)
ollama pull embeddinggemma:latest

# Verify the model is available
ollama list
```

**Model Specifications**:
- **Parameters**: 308M
- **Output Dimensions**: 768 (default), supports 512/256/128 via MRL
- **Context Length**: 2K tokens
- **Languages**: 100+ supported
- **RAM Usage**: <200MB with quantization

### Step 4: Verify SQLite Version

```bash
python -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Should show 3.35 or higher. If lower, upgrade Python or use a newer Python distribution.

## Configuration

### Environment Variables

Enable semantic search by setting these environment variables in your MCP configuration:

#### ENABLE_SEMANTIC_SEARCH (Required)

- **Type**: Boolean
- **Default**: `false`
- **Description**: Master switch for semantic search functionality
- **Example**: `"ENABLE_SEMANTIC_SEARCH": "true"`

#### OLLAMA_HOST (Optional)

- **Type**: String (URL)
- **Default**: `http://localhost:11434`
- **Description**: Ollama API endpoint for embedding generation
- **Example**: `"OLLAMA_HOST": "http://localhost:11434"`

**Docker Networking**: Use `host.docker.internal:11434` (Windows/macOS) or `172.17.0.1:11434` (Linux) when running in containers.

#### EMBEDDING_MODEL (Optional)

- **Type**: String
- **Default**: `embeddinggemma:latest`
- **Description**: Embedding model identifier
- **Alternatives**: `embeddinggemma:300m`, `nomic-embed-text`, `mxbai-embed-large`
- **Example**: `"EMBEDDING_MODEL": "embeddinggemma:latest"`

#### EMBEDDING_DIM (Optional)

- **Type**: Integer
- **Default**: `768`
- **Description**: Vector dimensions for embeddings
- **Valid Values**: 768, 512, 256, 128 (EmbeddingGemma supports Matryoshka Representation Learning)
- **Example**: `"EMBEDDING_DIM": "768"`

### MCP Configuration Example

Add to your `.mcp.json` file:

```json
{
  "mcpServers": {
    "context-server": {
      "type": "stdio",
      "command": "uvx",
      "args": [
        "--with",
        "mcp-context-server[semantic-search]",
        "mcp-context-server"
      ],
      "env": {
        "ENABLE_SEMANTIC_SEARCH": "true",
        "OLLAMA_HOST": "http://localhost:11434",
        "EMBEDDING_MODEL": "embeddinggemma:latest",
        "EMBEDDING_DIM": "768"
      }
    }
  }
}
```

### Alternative Models

While EmbeddingGemma is the default, Ollama supports other embedding models:

- **nomic-embed-text**: 768-dim, strong performance, English-focused
- **mxbai-embed-large**: 1024-dim, high quality, slower
- **all-minilm**: 384-dim, very fast, good for large-scale

Change via `EMBEDDING_MODEL` environment variable and adjust `EMBEDDING_DIM` accordingly.

## Changing Embedding Dimensions

**IMPORTANT**: Changing embedding dimensions requires database migration and will result in loss of existing embeddings.

### Understanding Dimension Compatibility

The embedding dimension (`EMBEDDING_DIM`) is fixed when the database is first created. The sqlite-vec extension creates vector tables with a specific dimension that cannot be changed after creation. If you need to use a different dimension:

1. **Existing embeddings will be incompatible** with the new dimension
2. **The database must be recreated** with the new dimension
3. **All embeddings will need to be regenerated** from context entries

### Common Embedding Dimensions by Model

| Model | Dimension | Notes |
|-------|-----------|-------|
| embeddinggemma:latest | 768 | Default, good general-purpose |
| nomic-embed-text | 768 | Strong performance, English-focused |
| mxbai-embed-large | 1024 | Higher quality, slower |
| all-minilm | 384 | Very fast, good for large-scale |

### Migration Procedure

When you change `EMBEDDING_DIM` and restart the server, you'll see this error:

```
RuntimeError: Embedding dimension mismatch detected!
  Existing database dimension: 768
  Configured EMBEDDING_DIM: 1024

To change embedding dimensions, you must:
  1. Back up your database: /path/to/context_storage.db
  2. Delete or rename the database file
  3. Restart the server to create new tables with dimension 1024
  4. Re-import your context data (embeddings will be regenerated)

Note: Changing dimensions will lose all existing embeddings.
```

**Step-by-step migration**:

1. **Back up your database** (Windows example):
   ```powershell
   copy %USERPROFILE%\.mcp\context_storage.db %USERPROFILE%\.mcp\context_storage.backup.db
   ```

2. **Stop the MCP server** (close Claude Desktop or stop the process)

3. **Update environment variable**:
   ```bash
   # In your .env file or environment
   EMBEDDING_DIM=1024  # New dimension
   EMBEDDING_MODEL=mxbai-embed-large  # Model that produces 1024-dim vectors
   ```

4. **Delete or rename the database**:
   ```powershell
   # Windows
   del %USERPROFILE%\.mcp\context_storage.db

   # Or rename to keep as backup
   move %USERPROFILE%\.mcp\context_storage.db %USERPROFILE%\.mcp\context_storage.old.db
   ```

5. **Restart the server** - it will create new tables with the configured dimension

6. **Re-import context data** - embeddings will be generated automatically when contexts are accessed via semantic search

### Validation and Error Messages

The server performs several validations:

1. **Dimension Range Check** (at startup):
   - `EMBEDDING_DIM` must be between 1 and 4096
   - Warning if not divisible by 64 (most models use 64-aligned dimensions)

2. **Compatibility Check** (at startup):
   - Compares configured dimension with existing database dimension
   - Raises error with migration instructions if mismatch detected

3. **Model Output Check** (at runtime):
   - Validates that model produces vectors of expected dimension
   - Raises clear error if model output doesn't match configuration

**Example validation error**:
```
ValueError: Embedding dimension mismatch: expected 1024, got 768.
This likely indicates a model mismatch.
Ensure EMBEDDING_MODEL (mxbai-embed-large) produces 1024-dimensional vectors,
or update EMBEDDING_DIM to match your model output.
```

### Best Practices

1. **Choose dimension based on your model**: Always set `EMBEDDING_DIM` to match your model's output
2. **Test before migrating production**: Use a separate test database to verify model compatibility
3. **Document your configuration**: Keep track of which model and dimension you're using
4. **Plan for data loss**: Understand that dimension changes require full re-embedding
5. **Consider performance**: Higher dimensions (1024) are more accurate but slower than lower dimensions (384, 512)

## Usage

### New Tool: semantic_search_tool

When semantic search is enabled and all dependencies are met, a new MCP tool becomes available.

**Parameters**:
- `query` (str, required): Natural language search query
- `top_k` (int, optional): Number of results to return (1-100, default: 20)
- `thread_id` (str, optional): Filter results to specific thread
- `source` (str, optional): Filter by source type ('user' or 'agent')

**Returns**:
```json
{
  "query": "original search query",
  "results": [
    {
      "id": 123,
      "thread_id": "thread-abc",
      "text_content": "matching context",
      "distance": 0.234,
      "tags": ["tag1", "tag2"]
    }
  ],
  "count": 5,
  "model": "embeddinggemma:latest"
}
```

**Distance Metric**: L2 (Euclidean distance) - lower values indicate higher similarity.

### Automatic Embedding Generation

Embeddings are generated automatically for stored context:

- **On `store_context`**: Embeddings generated in background (non-blocking)
- **On `update_context`**: Embeddings regenerated when text changes
- **On `delete_context`**: Embeddings cascade deleted automatically

If embedding generation fails, the context is still stored successfully (graceful degradation).

### Example Use Cases

1. **Cross-thread discovery**: Find related work from other sessions
   ```
   semantic_search_tool(query="authentication implementation", top_k=10)
   ```

2. **Agent collaboration**: Find what other agents learned
   ```
   semantic_search_tool(query="API rate limiting solutions", source="agent")
   ```

3. **Filtered search**: Combine semantic and structured filters
   ```
   semantic_search_tool(query="error handling", thread_id="current-task", top_k=5)
   ```

### Performance Characteristics

- **Embedding Generation**: 50-150ms per text (single), 200-500ms (batch of 10)
- **Similarity Search**: O(n * d) where n = filtered entries, d = 768
- **Acceptable Scale**: <100K context entries
- **Storage Impact**: ~3KB per embedding (768 floats × 4 bytes)

## Verification

### Complete Setup Checklist

Run through this checklist to verify your semantic search installation:

1. **Verify Ollama installation**:
   ```bash
   ollama --version
   ```

2. **Verify Ollama service**:
   ```bash
   curl http://localhost:11434
   # Should return: Ollama is running
   ```

3. **Verify model availability**:
   ```bash
   ollama list
   # Should show: embeddinggemma:latest
   ```

4. **Verify Python packages**:
   ```bash
   python -c "import ollama, numpy, sqlite_vec; print('All imports successful')"
   ```

5. **Verify SQLite extension support** (macOS only):
   ```python
   import sqlite3
   conn = sqlite3.connect(':memory:')
   print(hasattr(conn, 'enable_load_extension'))  # Should be True
   ```

6. **Start server with semantic search enabled**:
   ```bash
   # Set environment variable
   export ENABLE_SEMANTIC_SEARCH=true  # Linux/macOS
   set ENABLE_SEMANTIC_SEARCH=true     # Windows

   # Start server
   uv run mcp-context-server
   ```

7. **Check server logs** for:
   ```
   ✓ All semantic search dependencies available
   ✓ Semantic search enabled and available
   ✓ semantic_search_tool registered and exposed
   ```

8. **Verify MCP client** - List available tools and confirm `semantic_search_tool` is present

9. **Test functionality**:
    ```
    semantic_search_tool(query="test", top_k=5)
    ```

## Troubleshooting

### Issue 1: macOS Extension Support Error

**Error**: `AttributeError: 'sqlite3.Connection' object has no attribute 'enable_load_extension'`

**Cause**: Default macOS Python lacks SQLite extension support

**Solution**:
```bash
# Install Homebrew Python
brew install python

# Create new virtual environment with Homebrew Python
/opt/homebrew/bin/python3 -m venv .venv
source .venv/bin/activate

# Reinstall dependencies
uv sync --extra semantic-search
```

**Verification**:
```python
import sqlite3
conn = sqlite3.connect(':memory:')
print(hasattr(conn, 'enable_load_extension'))  # Must be True
```

### Issue 2: Ollama Connection Refused

**Error**: `Failed to connect to Ollama: Connection refused`

**Causes**:
- Ollama service not running
- Firewall blocking port 11434
- Docker networking misconfiguration

**Solutions**:

1. **Verify service is running**:
   ```bash
   curl http://localhost:11434
   # Should return: Ollama is running
   ```

2. **Start Ollama service**:
   - Windows: Launch Ollama app or run `ollama serve`
   - macOS: Launch Ollama from Applications
   - Linux: `systemctl start ollama` or `ollama serve`

3. **Check firewall** (Windows):
   - Allow incoming connections on port 11434
   - Add exception in Windows Defender

4. **Docker networking**:
   - Use `OLLAMA_HOST=http://host.docker.internal:11434` (Windows/macOS)
   - Use `OLLAMA_HOST=http://172.17.0.1:11434` (Linux)

### Issue 3: Model Not Found

**Error**: `Model 'embeddinggemma:latest' not found`

**Cause**: Model not downloaded

**Solution**:
```bash
# Pull the model
ollama pull embeddinggemma:latest

# Verify installation
ollama list
```

### Issue 4: semantic_search_tool Not Available

**Error**: `semantic_search_tool not available` or tool not listed

**Diagnostic Steps**:

1. **Check environment variable**:
   ```bash
   echo $ENABLE_SEMANTIC_SEARCH  # Linux/macOS
   echo %ENABLE_SEMANTIC_SEARCH% # Windows
   # Must show: true
   ```

2. **Check server logs** for dependency check messages:
   - Look for "✓ All semantic search dependencies available"
   - Or error messages indicating which dependency failed

3. **Call `get_statistics` tool**:
   - Check `semantic_search.available` field in response
   - Review any error messages

**Solution**: Fix the failing dependency based on error messages, then restart the server.

### Issue 5: Embedding Generation Timeout

**Error**: `Failed to generate embedding: timeout`

**Causes**:
- Ollama service overloaded
- Model not loaded in memory
- Insufficient RAM

**Solutions**:

1. **Check loaded models**:
   ```bash
   ollama ps
   # Shows currently loaded models
   ```

2. **Verify RAM availability**:
   - EmbeddingGemma needs ~200MB
   - Check system memory usage

3. **Increase model keep-alive**:
   ```bash
   export OLLAMA_KEEP_ALIVE=3600  # Keep model loaded for 1 hour
   ```

### Performance Optimization

1. **Increase parallel requests**:
   ```bash
   export OLLAMA_NUM_PARALLEL=8
   ```

2. **Keep model in memory longer**:
   ```bash
   export OLLAMA_KEEP_ALIVE=3600  # Seconds
   ```

3. **Use smaller dimensions** (trade-off: speed vs accuracy):
   ```json
   "EMBEDDING_DIM": "512"
   ```

4. **GPU acceleration**: Ollama automatically uses available GPU if detected

### Common Error Messages

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `ollama package is required` | Python package not installed | `uv sync --extra semantic-search` |
| `sqlite_vec package is required` | Python package not installed | `uv sync --extra semantic-search` |
| `Failed to connect to Ollama` | Service not running | Start Ollama service |
| `Model not found` | Model not pulled | `ollama pull embeddinggemma:latest` |
| `extension failed to load` | SQLite lacks extension support | Use Homebrew Python (macOS) |
| `Semantic search is not available` | Dependencies not met | Check server logs, fix dependencies |

## Additional Resources

### Official Documentation

- **Ollama**: [ollama.com](https://ollama.com)
- **EmbeddingGemma**: [ai.google.dev/gemma/docs/embeddinggemma](https://ai.google.dev/gemma/docs/embeddinggemma)
- **sqlite-vec**: [alexgarcia.xyz/sqlite-vec](https://alexgarcia.xyz/sqlite-vec)

### Model Information

- **Ollama Model Library**: [ollama.com/library/embeddinggemma](https://ollama.com/library/embeddinggemma)
- **HuggingFace**: [huggingface.co/google/embeddinggemma-300m](https://huggingface.co/google/embeddinggemma-300m)

### Troubleshooting Guides

- **SQLite Extensions on macOS**: [til.simonwillison.net/sqlite/sqlite-extensions-python-macos](https://til.simonwillison.net/sqlite/sqlite-extensions-python-macos)
- **sqlite-vec Python Integration**: [alexgarcia.xyz/sqlite-vec/python.html](https://alexgarcia.xyz/sqlite-vec/python.html)
