/**
 * georoset/docs/js/math.js
 * Toda a matemática de rotação e conversão portada para JavaScript.
 * Sistema de coordenadas: X=Leste, Y=Norte, Z=Cima (dextrogiro).
 */

const D2R = Math.PI / 180;
const R2D = 180 / Math.PI;

// ─── Matrizes 3×3 ────────────────────────────────────────────────────────────

function matMul(A, B) {
  const C = [[0,0,0],[0,0,0],[0,0,0]];
  for (let i = 0; i < 3; i++)
    for (let j = 0; j < 3; j++)
      for (let k = 0; k < 3; k++)
        C[i][j] += A[i][k] * B[k][j];
  return C;
}

function rotX(deg) {
  const t = deg * D2R, c = Math.cos(t), s = Math.sin(t);
  return [[1,0,0],[0,c,-s],[0,s,c]];
}
function rotY(deg) {
  const t = deg * D2R, c = Math.cos(t), s = Math.sin(t);
  return [[c,0,s],[0,1,0],[-s,0,c]];
}
function rotZ(deg) {
  const t = deg * D2R, c = Math.cos(t), s = Math.sin(t);
  return [[c,-s,0],[s,c,0],[0,0,1]];
}

function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

// ─── Decomposição Z-X-Z ──────────────────────────────────────────────────────

function matrixToEulerZXZ(R) {
  const r33 = clamp(R[2][2], -1, 1);
  const beta = Math.acos(r33) * R2D;
  const sb   = Math.sin(beta * D2R);
  let alpha, gamma;
  if (Math.abs(sb) < 1e-9) {
    alpha = 0;
    gamma = (r33 > 0
      ? Math.atan2(R[1][0], R[0][0])
      : Math.atan2(-R[1][0], R[0][0])) * R2D;
  } else {
    alpha = Math.atan2( R[0][2], -R[1][2]) * R2D;
    gamma = Math.atan2( R[2][0],  R[2][1]) * R2D;
  }
  return [((alpha % 360) + 360) % 360, beta, ((gamma % 360) + 360) % 360];
}

// ─── Decomposição X-Y-Z ──────────────────────────────────────────────────────

function matrixToEulerXYZ(R) {
  const val  = clamp(R[0][2], -1, 1);
  const beta = Math.asin(val) * R2D;
  const cb   = Math.cos(beta * D2R);
  let alpha, gamma;
  if (Math.abs(cb) < 1e-9) {
    gamma = 0;
    alpha = (val > 0
      ? Math.atan2( R[1][0],  R[1][1])
      : Math.atan2(-R[1][0],  R[1][1])) * R2D;
  } else {
    alpha = Math.atan2(-R[1][2], R[2][2]) * R2D;
    gamma = Math.atan2(-R[0][1], R[0][0]) * R2D;
  }
  return [alpha, beta, gamma];
}

// ─── Discos estruturais ───────────────────────────────────────────────────────

/** Leapfrog/Isatis: dip + dipDirection → vetor normal (X=E,Y=N,Z=Up) */
function dipDirToNormal(dip, dipDir) {
  const dr = dip * D2R, ar = dipDir * D2R;
  return [-Math.sin(dr)*Math.sin(ar), -Math.sin(dr)*Math.cos(ar), Math.cos(dr)];
}

/** Vetor normal → dip + dipDirection */
function normalToDipDir(n) {
  const nz  = clamp(n[2], -1, 1);
  const dip = Math.acos(nz) * R2D;
  const dd  = (Math.atan2(-n[0], -n[1]) * R2D + 360) % 360;
  return [dip, dd];
}

/** Vulcan: bearing + plunge da normal → vetor normal */
function vulcanDiscToNormal(bearing, plunge) {
  const br = bearing * D2R, pr = plunge * D2R;
  return [Math.cos(pr)*Math.sin(br), Math.cos(pr)*Math.cos(br), Math.sin(pr)];
}

/** Vetor normal → Vulcan bearing + plunge */
function normalToVulcanDisc(n) {
  const nz     = clamp(n[2], -1, 1);
  const plunge = Math.asin(nz) * R2D;
  const bearing = (Math.atan2(n[0], n[1]) * R2D + 360) % 360;
  return [bearing, plunge];
}

// ─── Conversões de disco ─────────────────────────────────────────────────────

function leapfrogToVulcanDisc(dip, dd) {
  return normalToVulcanDisc(dipDirToNormal(dip, dd));
}
function vulcanToLeapfrogDisc(bearing, plunge) {
  return normalToDipDir(vulcanDiscToNormal(bearing, plunge));
}

// ─── Variograma ───────────────────────────────────────────────────────────────

function leapfrogVarioMatrix(bearing, plunge, rake) {
  return matMul(matMul(rotZ(-bearing), rotX(-plunge)), rotZ(rake));
}
function vulcanVarioMatrix(bearing, plunge, dip) {
  return matMul(matMul(rotX(bearing), rotY(plunge)), rotZ(dip));
}
function isatisVarioMatrix(azimuth, dip, rake) {
  // R = Rz(−α)·Rx(−β)·Rx(ω)   ⚠️ sinal de β a confirmar (ISATIS_NEO_SIGN_CONVENTION = -1)
  return matMul(matMul(rotZ(-azimuth), rotX(-dip)), rotX(rake));
}

function matrixToLeapfrogVario(R) {
  // R = Rz(-α)·Rx(-β)·Rz(γ)  →  Rz(α)·R = Rx(-β)·Rz(γ)
  const col2 = [R[0][2], R[1][2], R[2][2]];
  const beta_r = Math.acos(clamp(col2[2], -1, 1));
  const sb = Math.sin(beta_r);
  let alpha, gamma;
  if (Math.abs(sb) < 1e-9) {
    alpha = 0;
    gamma = (col2[2] > 0
      ? Math.atan2(R[1][0], R[0][0])
      : Math.atan2(-R[1][0], R[0][0])) * R2D;
  } else {
    alpha = (Math.atan2( col2[0], -col2[1]) * R2D + 360) % 360;
    gamma = (Math.atan2( R[2][0],  R[2][1]) * R2D + 360) % 360;
  }
  const bearing = ((-alpha) % 360 + 360) % 360;
  const plunge  = ((-beta_r * R2D) % 360 + 360) % 360;
  return [bearing, plunge, ((gamma % 360) + 360) % 360];
}
function matrixToVulcanVario(R) { return matrixToEulerXYZ(R); }

// ─── Modelo de blocos ─────────────────────────────────────────────────────────

function leapfrogBlockMatrix(bearing, plunge, dip) {
  return matMul(matMul(rotZ(bearing), rotX(plunge)), rotZ(dip));
}
function vulcanBlockMatrix(bearing, plunge, dip) {
  return matMul(matMul(rotX(bearing), rotY(plunge)), rotZ(dip));
}
function isatisBlockMatrix(az, dip, rake) {
  return matMul(matMul(rotZ(az), rotX(dip)), rotZ(rake));
}

function matrixToLeapfrogBlock(R) { return matrixToEulerZXZ(R); }
function matrixToVulcanBlock(R)   { return matrixToEulerXYZ(R); }
function matrixToIsatisBlock(R)   { return matrixToEulerZXZ(R); }

// ─── Helpers de CSV ───────────────────────────────────────────────────────────

function downloadCSV(rows, headers, filename) {
  const lines = [headers.join(','), ...rows.map(r => r.map(v =>
    typeof v === 'number' ? v.toFixed(4) : v).join(','))];
  const blob = new Blob([lines.join('\n')], { type: 'text/csv' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

function parseCSV(text) {
  const lines = text.trim().split('\n').filter(l => l.trim());
  if (!lines.length) return { headers: [], rows: [] };
  const headers = lines[0].split(',').map(h => h.trim().replace(/"/g,''));
  const rows = lines.slice(1).map(l =>
    l.split(',').map(v => v.trim().replace(/"/g,''))
  );
  return { headers, rows };
}
