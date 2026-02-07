import { createRouter } from '@agentuity/runtime';
import type { Context } from 'hono';

const router = createRouter();

const backendBase = (process.env.JIRI_BACKEND_URL ?? 'http://127.0.0.1:8000').replace(/\/$/, '');

async function proxy(c: Context, path: string, init?: RequestInit) {
	const url = `${backendBase}${path}`;

	try {
		const response = await fetch(url, {
			...init,
			signal: AbortSignal.timeout(15000),
			headers: {
				accept: 'application/json',
				...(init?.headers ?? {}),
			},
		});

		const body = await response.text();
		const contentType = response.headers.get('content-type') ?? 'application/json';

		return new Response(body, {
			status: response.status,
			headers: { 'content-type': contentType },
		});
	} catch (error) {
		c.var.logger.error('Jiri backend proxy failed: %s', error instanceof Error ? error.message : String(error));
		return c.json(
			{
				error: 'backend_unreachable',
				message: 'Could not reach Jiri backend',
			},
			502,
		);
	}
}

router.get('/health', async (c) => proxy(c, '/health', { method: 'GET' }));

router.post('/turn', async (c) => {
	const payload = await c.req.json();
	return proxy(c, '/turn', {
		method: 'POST',
		headers: { 'content-type': 'application/json' },
		body: JSON.stringify(payload),
	});
});

router.get('/session/:sessionId/history', async (c) => {
	const sessionId = c.req.param('sessionId');
	return proxy(c, `/session/${encodeURIComponent(sessionId)}/history`, { method: 'GET' });
});

export default router;
