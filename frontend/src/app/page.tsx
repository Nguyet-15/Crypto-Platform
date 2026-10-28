"use client";
import { useEffect, useState } from 'react';
import { getHealth, getReadiness, getModules } from '@/services/api-client';
import type { ModuleStatus } from '@/types/api';

export default function Home() {
  const [health, setHealth] = useState('Đang kiểm tra API...');
  const [database, setDatabase] = useState('Đang kiểm tra PostgreSQL...');
  const [modules, setModules] = useState<ModuleStatus[]>([]);
  const [moduleError, setModuleError] = useState('');
  useEffect(() => {
    const controller = new AbortController();
    const signal = controller.signal;
    getHealth(signal).then((data) => { if (!signal.aborted) setHealth(`Đã kết nối: ${data.service} (${data.version})`); })
      .catch((error: Error) => { if (!signal.aborted) setHealth(error.message); });
    getReadiness(signal).then(() => { if (!signal.aborted) setDatabase('PostgreSQL đã sẵn sàng'); })
      .catch((error: Error) => { if (!signal.aborted) setDatabase(`PostgreSQL chưa sẵn sàng: ${error.message}`); });
    getModules(signal).then((data) => { if (!signal.aborted) setModules(data); })
      .catch((error: Error) => { if (!signal.aborted) setModuleError(error.message); });
    return () => controller.abort();
  }, []);
  return <main className="mx-auto max-w-5xl px-6 py-16">
    <p className="text-sm uppercase tracking-widest text-cyan-400">Foundation · v0.1</p>
    <h1 className="mt-4 text-4xl font-bold">Crypto AI Analysis Platform</h1>
    <p className="mt-4 max-w-2xl text-slate-400">Nền tảng nghiên cứu Crypto. Chưa triển khai dữ liệu thị trường, phân tích hoặc giao dịch bằng tiền thật.</p>
    <section className="mt-10 rounded-xl border border-slate-700 bg-slate-900 p-6" aria-live="polite">
      <h2 className="text-lg font-semibold">Kết nối hệ thống</h2>
      <p className="mt-2">{health}</p><p className="mt-2">{database}</p>
    </section>
    {moduleError && <p role="alert" className="mt-4">Không đọc được danh sách module: {moduleError}</p>}
    <div className="mt-6 grid gap-4 md:grid-cols-3">{modules.map((module) =>
      <section key={module.name} className="rounded-xl border border-slate-800 p-5">
        <h2 className="font-medium">{module.name}</h2>
        <p className="mt-2 text-sm text-slate-400">Chưa triển khai</p>
        <p className="mt-2 text-sm text-slate-500">{module.description}</p>
      </section>)}</div>
  </main>;
}
