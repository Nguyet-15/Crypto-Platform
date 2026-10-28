import { test } from 'node:test';
import assert from 'node:assert/strict';
import api from '../.test-build/services/api-client.js';
const { createApiClient, ApiError } = api;

test('health validates response and joins URL', async () => {
  const client = createApiClient({ baseUrl: 'http://localhost/api/v1/', fetcher: async (url, options) => {
    assert.equal(url, 'http://localhost/api/v1/health');
    assert.equal(options.cache, 'no-store');
    return Response.json({ status: 'ok', service: 'api', version: '1' });
  }});
  assert.equal((await client.getHealth()).service, 'api');
});

test('HTTP failures preserve status and request ID', async () => {
  const client = createApiClient({ fetcher: async () => new Response('', {
    status: 503, headers: { 'X-Request-ID': 'test-request' },
  }) });
  await assert.rejects(client.getReadiness(), (error) =>
    error instanceof ApiError && error.status === 503 && error.requestId === 'test-request');
});

test('rejects malformed response and network errors', async () => {
  await assert.rejects(createApiClient({ fetcher: async () => Response.json({ status: 'ok' }) }).getHealth(), /Invalid API response/);
  await assert.rejects(createApiClient({ fetcher: async () => { throw new Error('private'); } }).getHealth(), /Cannot connect/);
});

test('timeout aborts pending request', async () => {
  const client = createApiClient({ timeoutMs: 5, fetcher: (_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new Error('aborted')), { once: true });
  }) });
  await assert.rejects(client.getHealth(), /timed out/);
});

test('validates module status and readiness contracts', async () => {
  const ready = createApiClient({ fetcher: async () => Response.json({ status: 'ready', database: 'ok' }) });
  assert.equal((await ready.getReadiness()).database, 'ok');
  const invalid = createApiClient({ fetcher: async () => Response.json([{ name: 'smc', status: 'implemented', description: '' }]) });
  await assert.rejects(invalid.getModules(), /Invalid API response/);
});

test('caller can cancel an active request', async () => {
  const controller = new AbortController();
  const client = createApiClient({ fetcher: (_url, options) => new Promise((_resolve, reject) => {
    options.signal.addEventListener('abort', () => reject(new Error('aborted')), { once: true });
  }) });
  const pending = client.getHealth(controller.signal);
  controller.abort();
  await assert.rejects(pending, /cancelled/);
});
