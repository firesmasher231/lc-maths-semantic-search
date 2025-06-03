# Memory Optimization Guide

## 🎯 Goal: Reduce Memory Usage from 1.5GB to ~400-600MB

### Key Optimizations Implemented

1. **CPU-Only PyTorch Configuration** (saves ~300-500MB)

   - Force CPU-only execution with environment variables
   - Reduce thread usage to minimize memory overhead
   - Disable unnecessary parallelism features

2. **Smaller Model** (saves ~60MB)

   - Changed from `all-MiniLM-L6-v2` (80MB) to `paraphrase-MiniLM-L3-v2` (17MB)
   - Still maintains good search quality

3. **Embeddings Caching** (reduces startup memory)

   - Embeddings saved to disk after first processing
   - Faster subsequent startups without memory spikes

4. **Lazy Model Loading** (saves ~100MB during idle)

   - Model only loaded when needed for searches
   - Automatically unloaded after processing

5. **Thread & Process Optimization** (saves ~50-100MB)

   - Single-threaded PyTorch operations
   - Reduced OpenMP/MKL thread counts
   - Disabled tokenizer parallelism

6. **Garbage Collection** (frees unused memory)
   - Automatic cleanup after searches
   - Manual cleanup endpoint available

## 📋 Deployment Steps

### 1. Deploy with Standard PyTorch

The optimizations are now deployment-friendly and don't require special PyTorch versions.

### 2. Monitor Memory Usage

**Check memory status:**

```bash
curl http://your-domain/api/memory
```

**Force cleanup if needed:**

```bash
curl -X POST http://your-domain/api/cleanup
```

## 📊 Expected Results

| Component    | Before        | After          | Savings     |
| ------------ | ------------- | -------------- | ----------- |
| PyTorch Base | ~800MB        | ~300MB         | ~500MB      |
| Model        | ~80MB         | ~17MB          | ~63MB       |
| Threading    | ~100MB        | ~20MB          | ~80MB       |
| Embeddings   | Always in RAM | Cached to disk | Variable    |
| **Total**    | **~1.5GB**    | **~400-600MB** | **~60-70%** |

## 🔍 Monitoring

### Memory Info Endpoint

`GET /api/memory` returns:

```json
{
  "gc_stats": {...},
  "model_loaded": false,
  "embeddings_loaded": true,
  "questions_count": 150,
  "processing_status": "Ready"
}
```

### Cleanup Endpoint

`POST /api/cleanup` performs:

- Multiple garbage collection rounds
- Model unloading if loaded
- Memory defragmentation

## 🚨 Troubleshooting

### If Memory Usage is Still High:

1. Check if model is persistently loaded: `GET /api/memory`
2. Force cleanup: `POST /api/cleanup`
3. Clear cache and restart the application

### If Search Performance Degrades:

- The smaller model might have slightly lower accuracy
- Can switch back to `all-MiniLM-L6-v2` in `config.py` if needed
- Single-threading may make searches slightly slower but saves memory

## 💰 Hosting Cost Impact

**Before:** 1.5GB RAM tier  
**After:** 512MB-1GB RAM tier  
**Savings:** ~40-60% on hosting costs

## 🔧 Technical Implementation

The optimizations work by:

1. **Environment Variables:** Force CPU-only mode before PyTorch loads
2. **Thread Limiting:** Reduce concurrent operations to save memory
3. **Model Caching:** Avoid reloading embeddings on each startup
4. **Lazy Loading:** Only load model when actually needed for search
5. **Garbage Collection:** Proactive cleanup of unused objects
