export function parseCoordinates(query) {
  const match = query.trim().match(/^([-+]?\d+(?:\.\d+)?)\s*[, ]\s*([-+]?\d+(?:\.\d+)?)$/)
    || query.match(/(?:@|[?&]q=|[?&]query=)(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)/);
  if (!match) return null;
  const [lat, lon] = match.slice(1).map(Number);
  return Math.abs(lat) <= 85 && Math.abs(lon) <= 180 ? [lat,lon] : null;
}

async function json(url) {
  const response = await fetch(url, {signal:AbortSignal.timeout(5500)});
  if (!response.ok) throw Error('Geocoder unavailable');
  return response.json();
}

export async function lookupLocation(query) {
  const q = encodeURIComponent(query);
  const results = await Promise.allSettled([
    json('https://photon.komoot.io/api/?limit=8&q='+q).then(data => data.features.map(f => {
      const p = f.properties;
      return {coords:f.geometry.coordinates.slice(0,2).reverse(),
        label:[...new Set([p.name, [p.housenumber,p.street].filter(Boolean).join(' '),p.district,p.city,p.county,p.state,p.postcode,p.country].filter(Boolean))].join(', '),
        source:'Photon / OpenStreetMap'};
    })),
    json('https://nominatim.openstreetmap.org/search?format=jsonv2&limit=8&q='+q)
      .then(data => data.map(r => ({coords:[Number(r.lat),Number(r.lon)],label:r.display_name,source:'Nominatim / OpenStreetMap'})))
  ]);
  const found = [];
  for (const result of results) {
    if (result.status !== 'fulfilled') continue;
    for (const item of result.value) {
      if (!item.label || !item.coords.every(Number.isFinite)) continue;
      if (!found.some(r => Math.abs(r.coords[0]-item.coords[0])<0.00015 && Math.abs(r.coords[1]-item.coords[1])<0.00015)) found.push(item);
    }
  }
  return {found, unavailable:results.every(r => r.status === 'rejected')};
}
