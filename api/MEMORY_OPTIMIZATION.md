# Memory Optimization Guide

## 🎯 Goal: Reduce Memory Usage from 1.5GB to ~400-600MB

### Key Optimizations Implemented

1. **CPU-Only PyTorch** (saves ~500-800MB)

   - Switched from full PyTorch to CPU-only version
   - Removes GPU-related components that consume memory even when unused

2. **Smaller Model** (saves ~60MB)

   - Changed from `all-MiniLM-L6-v2` (80MB) to `paraphrase-MiniLM-L3-v2` (17MB)
   - Still maintains good search quality

3. **Embeddings Caching** (reduces startup memory)

   - Embeddings saved to disk after first processing
   - Faster subsequent startups without memory spikes

4. **Lazy Model Loading** (saves ~100MB during idle)

   - Model only loaded when needed for searches
   - Automatically unloaded after processing

5. **Garbage Collection** (frees unused memory)
   - Automatic cleanup after searches
   - Manual cleanup endpoint available

## 📋 Deployment Steps

### 1. Apply Optimizations

```bash
cd api
python optimize_memory.py --clear-cache --reinstall
```

### 2. Restart Your Application

```bash
# Stop current instance
# Restart with your normal process (gunicorn, python app.py, etc.)
```

### 3. Monitor Memory Usage

**Check memory status:**

```bash
curl http://your-domain/api/memory
```

**Force cleanup if needed:**

```bash
curl -X POST http://your-domain/api/cleanup
```

## 📊 Expected Results

| Component  | Before        | After          | Savings     |
| ---------- | ------------- | -------------- | ----------- |
| PyTorch    | ~800MB        | ~200MB         | ~600MB      |
| Model      | ~80MB         | ~17MB          | ~63MB       |
| Embeddings | Always in RAM | Cached to disk | Variable    |
| **Total**  | **~1.5GB**    | **~400-600MB** | **~60-70%** |

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
3. Clear cache and restart: `python optimize_memory.py --clear-cache`

### If Search Performance Degrades:

- The smaller model might have slightly lower accuracy
- Can switch back to `all-MiniLM-L6-v2` in `config.py` if needed
- Monitor search quality vs memory usage trade-off

## 💰 Hosting Cost Impact

**Before:** 1.5GB RAM tier
**After:** 512MB-1GB RAM tier
**Savings:** ~40-60% on hosting costs
