export type Health = { status: 'ok'; service: string; version: string };
export type Readiness = { status: 'ready'; database: 'ok' };
export type ModuleStatus = { name: string; status: 'not_implemented'; description: string };
