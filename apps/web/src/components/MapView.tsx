import { Fragment, useEffect } from "react";
import type { GeoJsonObject } from "geojson";
import {
  CircleMarker,
  GeoJSON,
  ImageOverlay,
  MapContainer,
  Polyline,
  Popup,
  TileLayer,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { AisPoint, AnalysisResult, GeoJsonFeature, SarBounds } from "../types";

type MapViewProps = {
  result: AnalysisResult | null;
  spillPolygon: GeoJsonFeature;
  sarBounds: SarBounds;
  sarImageUrl: string;
  selectedVesselId: string | null;
  onVesselSelect: (vesselId: string) => void;
  layers: string[];
  aisTracks: Record<string, AisPoint[]>;
  currentTime: string | null;
};

function MapFitter({ bounds }: { bounds: [[number, number], [number, number]] }) {
  const map = useMap();
  useEffect(() => { map.fitBounds(bounds, { padding: [36, 36] }); }, [bounds, map]);
  return null;
}

function geoJson(data: unknown) {
  return data as GeoJsonObject;
}

export function MapView({
  result,
  spillPolygon,
  sarBounds,
  sarImageUrl,
  selectedVesselId,
  onVesselSelect,
  layers,
  aisTracks,
  currentTime,
}: MapViewProps) {
  const bounds: [[number, number], [number, number]] = [
    [sarBounds.south, sarBounds.west],
    [sarBounds.north, sarBounds.east],
  ];
  const source = result?.source_region;
  const cutoff = currentTime ? new Date(currentTime).getTime() : Number.POSITIVE_INFINITY;

  return (
    <MapContainer center={[18.95, 69]} zoom={9} zoomControl={false} attributionControl>
      <TileLayer
        url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      <MapFitter bounds={bounds} />

      {layers.includes("sar_image") && <ImageOverlay url={sarImageUrl} bounds={bounds} opacity={0.82} />}

      {layers.includes("spill_polygon") && (
        <>
          <GeoJSON
            data={geoJson(spillPolygon)}
            style={{ color: "#f1b24b", weight: 1.5, dashArray: "7 5", fillColor: "#f1b24b", fillOpacity: 0.08 }}
          />
          {result && (
            <GeoJSON
              data={geoJson(result.detector.polygon)}
              style={{ color: "#f7f3e8", weight: 2.5, fillColor: "#0b1012", fillOpacity: 0.28 }}
            />
          )}
        </>
      )}

      {layers.includes("source_heatmap") && source && (
        <>
          <GeoJSON data={geoJson(source.low_probability)} style={{ color: "#ff6b35", weight: 1, fillColor: "#ff6b35", fillOpacity: 0.12 }} />
          <GeoJSON data={geoJson(source.medium_probability)} style={{ color: "#ff8f3f", weight: 1, fillColor: "#ff8f3f", fillOpacity: 0.22 }} />
          <GeoJSON data={geoJson(source.high_probability)} style={{ color: "#ffb15b", weight: 1.5, fillColor: "#ff9f43", fillOpacity: 0.38 }} />
          {source.heatmap_points.filter((point) => point.weight >= 0.8).map((point, index) => (
            <CircleMarker
              key={`${point.release_time}-${index}`}
              center={[point.latitude, point.longitude]}
              radius={3 + point.weight * 4}
              pathOptions={{ color: "#fff1d2", weight: 1, fillColor: "#ff7a36", fillOpacity: 0.85 }}
            />
          ))}
        </>
      )}

      {layers.includes("particle_paths") && result?.particles.map((path) => (
        <Polyline
          key={path.vessel_id}
          positions={path.points.map((point) => [point.latitude, point.longitude])}
          pathOptions={{ color: "#ff9f43", weight: 1.5, dashArray: "5 6", opacity: 0.62 }}
        />
      ))}

      {layers.includes("ais_tracks") && result && Object.entries(aisTracks).map(([vesselId, rawTrack], trackIndex) => {
        const track = rawTrack.filter((point) => new Date(point.timestamp).getTime() <= cutoff);
        if (track.length === 0) return null;
        const selected = selectedVesselId === vesselId;
        const colors = ["#36d2b4", "#77aafc", "#a3aab1"];
        const color = colors[trackIndex % colors.length];
        const last = track[track.length - 1];
        return (
          <Fragment key={vesselId}>
            <Polyline
              positions={track.map((point) => [point.latitude, point.longitude])}
              pathOptions={{ color, weight: selected ? 4 : 2.3, opacity: selected ? 1 : 0.72 }}
              eventHandlers={{ click: () => onVesselSelect(vesselId) }}
            />
            <CircleMarker
              center={[last.latitude, last.longitude]}
              radius={selected ? 7 : 5}
              pathOptions={{ color: "#071013", weight: 2, fillColor: color, fillOpacity: 1 }}
              eventHandlers={{ click: () => onVesselSelect(vesselId) }}
            >
              <Popup><strong>{last.name}</strong><br />MMSI {last.mmsi}<br />{last.vessel_type.replaceAll("_", " ")}</Popup>
            </CircleMarker>
          </Fragment>
        );
      })}
    </MapContainer>
  );
}
