/**
 * Cloudflare Worker for PDF Translation
 * Auto-generated setup
 */

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
    const url = new URL(request.url)

    // Proxy requests to Google Gemini
    if (url.pathname === '/translate') {
        return handleTranslation(request)
    }

    return new Response('PDF Translator Worker', { status: 200 })
}

async function handleTranslation(request) {
    const body = await request.json()
    const { text, apiKey } = body

    // Make request to Google Gemini
    const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            contents: [{
                parts: [{ text }]
            }]
        })
    })

    const data = await response.json()
    return new Response(JSON.stringify(data), {
        status: response.status,
        headers: { 'Content-Type': 'application/json' }
    })
}
