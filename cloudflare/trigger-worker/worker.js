// CuratorDailyNews tetikleyici Worker'ı (eski adı: wispy-grass-5ba7)
// GitHub Actions'taki daily_digest.yml workflow'unu workflow_dispatch ile tetikler.
export default {
  // 1. Cron tetikleyici (wrangler.toml'da crons açılırsa çalışır)
  async scheduled(event, env, ctx) {
    await triggerGitHubActions(env);
  },

  // 2. Tarayıcıdan tıklanınca çalışacak kısım
  async fetch(request, env, ctx) {
    const success = await triggerGitHubActions(env);
    if (success) {
      return new Response("🚀 GitHub Actions bülten akışı başarıyla tetiklendi!", { status: 200 });
    } else {
      return new Response("❌ Tetikleme başarısız oldu.", { status: 500 });
    }
  }
};

async function triggerGitHubActions(env) {
  const url = "https://api.github.com/repos/RYucel/CuratorDailyNews/actions/workflows/daily_digest.yml/dispatches";
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.GITHUB_PAT}`,
        "Accept": "application/vnd.github+json",
        "User-Agent": "Cloudflare-Cron"
      },
      body: JSON.stringify({ ref: "main" })
    });
    return res.ok;
  } catch (e) {
    return false;
  }
}
