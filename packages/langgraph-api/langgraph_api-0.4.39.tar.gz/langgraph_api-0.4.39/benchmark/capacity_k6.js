import http from 'k6/http';
import { sleep } from 'k6';
import { Trend, Counter, Rate } from 'k6/metrics';

// Mao

const baseUrlToBaseUrlName = {
  'https://ifh-core-api-dr-benchmark-048d364b548f5d9790082d8ba4fb44d8.us.langgraph.app': 'DRC,API S,OPS S',
  'https://ifh-benchmarks-ba3f7d811fb6564ebe5248bcd7a0a662.us.langgraph.app': 'API S, OPS S',
  'https://wfh-benchmark-distributed-r-1603f73b1a175234b9b0fb1f9beea4f1.us.langgraph.app': 'DR,API S,OPS S',
  "https://benchmark-api-m-ops-s-81bb8ca883ce54438fcb9027877be8e7.us.langgraph.app": "API M, OPS S",
  "https://benchmark-api-s-ops-m-32baf0b195b7589eb77ce06c373f0886.us.langgraph.app": "API S, OPS M",
  "https://benchmark-api-m-ops-m-2c4ecc0e7f6a526fac98db7068092d5a.us.langgraph.app": "API M, OPS M",
  "https://benchmark-dr-api-m-ops-s-d3bfd55b7b065af5a89d3b15edd99500.us.langgraph.app": "DR, API M, OPS S",
  "https://benchmark-dr-api-s-ops-m-7f98f893140257b7869cbe00a93ecb71.us.langgraph.app": "DR, API S, OPS M",
  "https://benchmark-dr-api-m-ops-m-22b1c77d9f175160b226090601add28a.us.langgraph.app": "DR, API M, OPS M",
  "https://benchmark-drc-api-m-ops-s-9a7d59e246d95b5bad994c7ea269c460.us.langgraph.app": "DRC, API M, OPS S",
  "https://benchmark-drc-api-s-ops-m-d54e214bd0fd5c9db1f44b80065f7b9a.us.langgraph.app": "DRC, API S, OPS M",
  "https://benchmark-drc-api-m-ops-m-caa32d5c7e945a15a3818aa7a941b1bd.us.langgraph.app": "DRC, API M, OPS M",
  "https://benchmark-dr-api-s-ops-s-db-b8ba0253c7a65ace836c0662f22c530d.us.langgraph.app": "DR, API S, OPS S, DB M",
  "https://benchmark-api-s-ops-s-db-m-4e3d4e6f27d35555b7f3955c3a4c301a.us.langgraph.app": "API S, OPS S, DB M",
  "https://benchmark-dr-api-s-ops-s-re-423b90208677556e86eced49b27a73a0.us.langgraph.app": "DR, API S, OPS S, Redis M",
  "https://benchmark-api-s-ops-s-redis-91911734773c51e292ecb2b15fa015e5.us.langgraph.app": "API S, OPS S, Redis M"
}

// Metrics
const runDuration = new Trend('run_duration'); // ms for successful runs
const runPickUpDuration = new Trend('run_pickup_duration');
const runReturnDuration = new Trend('run_return_duration');
const runInsertionDuration = new Trend('run_insertion_duration');
const runOSSDuration = new Trend('run_oss_duration');
const successfulRuns = new Counter('successful_runs');
const failedRuns = new Counter('failed_runs');
const capacitySuccessRate = new Rate('capacity_success_rate');

// Env
const BASE_URL = __ENV.BASE_URL;
const LANGSMITH_API_KEY = __ENV.LANGSMITH_API_KEY;

const TARGET = parseInt(__ENV.TARGET || '10');
const WAIT_SECONDS = parseInt(__ENV.WAIT_SECONDS || '60');
const SUCCESS_THRESHOLD = parseFloat(__ENV.SUCCESS_THRESHOLD || '0.99');

// Agent params
const DATA_SIZE = parseInt(__ENV.DATA_SIZE || '1000');
const DELAY = parseInt(__ENV.DELAY || '0');
const EXPAND = parseInt(__ENV.EXPAND || '10');
const STEPS = parseInt(__ENV.STEPS || '10');

// Options
export const options = {
  scenarios: {
    capacity_single_shot: {
      executor: 'shared-iterations',
      vus: TARGET,
      iterations: TARGET,
      maxDuration: `${Math.max(WAIT_SECONDS + 120, 150)}s`,
    },
  },
  thresholds: {
    'capacity_success_rate': [`rate>=${SUCCESS_THRESHOLD}`],
  },
};

function headers() {
  const h = { 'Content-Type': 'application/json' };
  if (LANGSMITH_API_KEY) h['x-api-key'] = LANGSMITH_API_KEY;
  return h;
}

function buildPayload() {
  return JSON.stringify({
    assistant_id: 'benchmark',
    input: {
      data_size: DATA_SIZE,
      delay: DELAY,
      expand: EXPAND,
      steps: STEPS,
    },
    config: {
      recursion_limit: STEPS + 2,
    },
  });
}

export default function () {
  // one-shot per iteration: create → wait → poll status once
  const payload = buildPayload();
  const reqHeaders = headers();

  let threadId;
  let runId;
  let createdAt;

  try {
    const tRes = http.post(`${BASE_URL}/threads`, payload, {
      headers: reqHeaders,
      timeout: '60s',
    });
    if (tRes.status !== 200) {
      failedRuns.add(1);
      capacitySuccessRate.add(0);
      return;
    }
    const t = tRes.json();
    threadId = t.thread_id;

    createdAt = new Date().getTime();
    const rRes = http.post(`${BASE_URL}/threads/${threadId}/runs`, payload, {
      headers: reqHeaders,
      timeout: '60s',
    });
    if (rRes.status !== 200) {
      failedRuns.add(1);
      capacitySuccessRate.add(0);
      return;
    }
    const r = rRes.json();
    runId = r.run_id;
  } catch (e) {
    // Any network error counts as a failure — no retries
    failedRuns.add(1);
    capacitySuccessRate.add(0);
    return;
  }

  // Sleep the configured wait time, exactly once
  sleep(WAIT_SECONDS);

  // Poll exactly once
  try {
    const gRes = http.get(`${BASE_URL}/threads/${threadId}/runs/${runId}`, {
      headers: reqHeaders,
      timeout: '30s',
    });
    const tRes = http.get(`${BASE_URL}/threads/${threadId}/state`, {
      headers: reqHeaders,
      timeout: '30s',
    });
    if (gRes.status !== 200) {
      failedRuns.add(1);
      capacitySuccessRate.add(0);
      return;
    }
    const run = gRes.json();
    const t = tRes.json();
    if (run.status === 'success') {
      successfulRuns.add(1);
      capacitySuccessRate.add(1);
      try {
        const insertionMs = new Date(run.created_at).getTime() - createdAt;
        if (!Number.isNaN(insertionMs) && insertionMs >= 0) {
          runInsertionDuration.add(insertionMs);
        }
        const durMs = new Date(run.updated_at).getTime() - createdAt;
        if (!Number.isNaN(durMs) && durMs >= 0) {
          runDuration.add(durMs);
        }
        const pickupDurMs = new Date(t.values.start_time).getTime() - new Date(run.created_at).getTime();
        if (!Number.isNaN(pickupDurMs) && pickupDurMs >= 0) {
          runPickUpDuration.add(pickupDurMs);
        }
        // Note: we are missing the time from `set_joint_status` to actually return to the client (ideally this is negligible)
        const returnDurMs = new Date(run.updated_at).getTime() - new Date(t.values.end_time).getTime();
        if (!Number.isNaN(returnDurMs) && returnDurMs >= 0) {
          runReturnDuration.add(returnDurMs);
        }
        const ossDurMs = new Date(t.values.end_time).getTime() - new Date(t.values.start_time).getTime();
        if (!Number.isNaN(ossDurMs) && ossDurMs >= 0) {
          runOSSDuration.add(ossDurMs);
        }
      } catch (_) {
        // ignore duration parsing errors
      }
    } else {
      failedRuns.add(1);
      capacitySuccessRate.add(0);
    }
  } catch (e) {
    failedRuns.add(1);
    capacitySuccessRate.add(0);
  }
}

export function handleSummary(data) {
  const ts = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');

  const total = (data.metrics.successful_runs?.values?.count || 0) + (data.metrics.failed_runs?.values?.count || 0);
  const succ = data.metrics.successful_runs?.values?.count || 0;
  const fail = data.metrics.failed_runs?.values?.count || 0;
  const successRate = total > 0 ? (succ / total) * 100 : 0;

  function withStats(metric) {
    if (!data.metrics[metric]?.values) return {};
    const vals = data.metrics[metric].values;
    return {
      avg: vals.avg ? vals.avg / 1000 : null,
      p50: vals.med ? vals.med / 1000 : null,
      p95: vals['p(95)'] ? vals['p(95)'] / 1000 : null,
      max: vals.max ? vals.max / 1000 : null,
    };
  }

  const summary = {
    timestamp: ts,
    settings: {
      baseUrl: BASE_URL,
      baseUrlName: baseUrlToBaseUrlName[BASE_URL],
      target: TARGET,
      waitSeconds: WAIT_SECONDS,
      dataSize: DATA_SIZE,
      delay: DELAY,
      expand: EXPAND,
      steps: STEPS,
    },
    metrics: {
      totalRuns: total,
      successfulRuns: succ,
      failedRuns: fail,
      successRate,
      runDuration: withStats('run_duration'),
      runPickupDuration: withStats('run_pickup_duration'),
      runReturnDuration: withStats('run_return_duration'),
      runInsertionDuration: withStats('run_insertion_duration'),
      runOSSDuration: withStats('run_oss_duration'),
    },
  };

  const fname = `capacity_summary_t${TARGET}_${ts}.json`;
  return {
    [fname]: JSON.stringify(summary, null, 2),
    stdout: JSON.stringify(summary),
  };
}
