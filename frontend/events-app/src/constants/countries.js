// Страны подгружаются с API /countries
// Этот файл используется как fallback
export const COUNTRY_CODES = [];

export async function loadCountries() {
  try {
    const res = await fetch('https://ranking.worldstrongman.org/countries');
    return await res.json();
  } catch {
    return [];
  }
}
