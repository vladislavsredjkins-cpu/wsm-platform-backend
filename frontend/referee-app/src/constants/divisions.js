export const DIVISION_LABELS = {
  MEN: 'Men', WOMEN: 'Women', PARA_MEN: 'Para Men', PARA_WOMEN: 'Para Women',
  SENIOR: 'Senior', JUNIOR: 'Junior', MASTERS40: 'Masters 40+', MASTERS50: 'Masters 50+',
  O110: 'Super Heavyweight (110kg+)', U110: 'Heavyweight (–110kg)',
  U95: 'Middleweight (–95kg)', U80: 'Lightweight (–80kg)', U70: 'Featherweight (–70kg)',
  O85: 'Super Heavyweight (85kg+)', U85: 'Heavyweight (–85kg)',
  U75: 'Middleweight (–75kg)', U65: 'Lightweight (–65kg)', U55: 'Featherweight (–55kg)',
  OPEN: 'Open', O80: 'Over 80kg',
};

export function divisionLabel(key) {
  if (!key) return '';
  const parts = key.split('_');
  let gender, rest;
  if (parts[0] === 'PARA') {
    gender = 'PARA_' + parts[1];
    rest = parts.slice(2);
  } else {
    gender = parts[0];
    rest = parts.slice(1);
  }
  const result = [DIVISION_LABELS[gender] || gender];
  rest.forEach(p => result.push(DIVISION_LABELS[p] || p));
  return result.join(' · ');
}
