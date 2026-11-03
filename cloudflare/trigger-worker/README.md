# Cloudflare tetikleyici Worker

`daily_digest.yml` workflow'unu dışarıdan tetikleyen küçük Worker. 2026-11-03'te Cloudflare'den kaldırıldı (eski adı `wispy-grass-5ba7`); kodu burada duruyor.

## Tekrar devreye almak

1. Actions > "Curator Daily News Digest & Site Generator" > **Enable workflow**.
2. Repo Settings > Secrets and variables > Actions altında şu secret'ları ekle:
   - `CLOUDFLARE_API_TOKEN`: "Edit Cloudflare Workers" şablonuyla oluşturulmuş token
   - `CLOUDFLARE_ACCOUNT_ID`: Cloudflare hesap ID'si
   - `WORKER_GITHUB_PAT`: bu repoda Actions: write yetkili fine-grained PAT
3. Actions > "Cloudflare tetikleyici Worker'ı yayınla" > **Run workflow**.

Cloudflare cron ile çalışması isteniyorsa `wrangler.toml` içindeki `[triggers]` bloğunu aç.
Not: `fetch` handler'ı URL'yi açan herkesin workflow'u tetiklemesine izin verir.
