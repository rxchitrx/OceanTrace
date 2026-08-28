import React, { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  GeoJSON,
  Polyline,
  CircleMarker,
  ImageOverlay,
  Popup,
  useMap,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { AnalysisResult, AisPoint } from "../types";

type MapViewProps = {
  result: AnalysisResult | null;
  spillPolygon: any | null;
  sarBounds: any | null;
  sarImageUrl: string | null;
  selectedVesselId: string | null;
  onVesselSelect: (vesselId: string) => void;
  layers: string[];
  aisTracks: Record<string, AisPoint[]> | null;
};

function MapFitter({ bounds }: { bounds: [[number, number], [number, number]] | null }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bounds, map]);
  return null;
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
}: MapViewProps) {
  const defaultCenter: [number, number] = [18.95, 69.0];

  let boundsToFit: [[number, number], [number, number]] | null = null;
  if (sarBounds) {
    boundsToFit = [
      [sarBounds.south, sarBounds.west],
      [sarBounds.north, sarBounds.east],
    ];
  } else if (spillPolygon) {
    const coords = spillPolygon.geometry.coordinates[0];
    const lats = coords.map((c: any) => c[1]);
    const lons = coords.map((c: any) => c[0]);
    boundsToFit = [
      [Math.min(...lats), Math.min(...lons)],
      [Math.max(...lats), Math.max(...lons)],
    ];
  }

  const showSar = layers.includes("sar_image") && sarImageUrl && sarBounds;
  const showPolygon = layers.includes("spill_polygon") && spillPolygon;
  const showHeatmap = layers.includes("source_heatmap") && result;
  const showParticles = layers.includes("particle_paths") && result;
  const showAis = layers.includes("ais_tracks") && result;

  return (
    <div style={{ height: "100%", width: "100%", borderRadius: "18px", overflow: "hidden", position: "absolute", top: 0, left: 0 }}>
      <MapContainer
        center={defaultCenter}
        zoom={10}
        style={{ height: "100%", width: "100%", backgroundColor: "#081317" }}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; OpenStreetMap &copy; CARTO'
        />

        <MapFitter bounds={boundsToFit} />

        {showSar && (
          <ImageOverlay
            url={sarImageUrl}
            bounds={[
              [sarBounds.south, sarBounds.west],
              [sarBounds.north, sarBounds.east],
            ]}
            opacity={0.8}
          />
        )}

        {showHeatmap && (
          <>
            <GeoJSON
              data={result.source_region.low_probability}
              style={{ color: "#d17c48", weight: 0, fillColor: "#d17c48", fillOpacity: 0.2 }}
            />
            <GeoJSON
              data={result.source_region.medium_probability}
              style={{ color: "#d17c48", weight: 0, fillColor: "#d17c48", fillOpacity: 0.4 }}
            />
            <GeoJSON
              data={result.source_region.high_probability}
              style={{ color: "#d17c48", weight: 0, fillColor: "#d17c48", fillOpacity: 0.6 }}
            />
            {result.source_region.heatmap_points.map((pt, i) => (
              <CircleMarker
                key={i}
                center={[pt.latitude, pt.longitude]}
                radius={pt.weight * 10}
                pathOptions={{ color: "#fff", weight: 1, fillColor: "#d17c48", fillOpacity: 0.8 }}
              />
            ))}
          </>
        )}

        {showParticles &&
          result.particles.map((path, idx) => (
            <Polyline
              key={`particle-${idx}`}
              positions={path.points.map((p) => [p.latitude, p.longitude])}
              pathOptions={{ color: "#ff8e78", weight: 2, dashArray: "4 4", opacity: 0.6 }}
            />
          ))}

        {showPolygon && (
          <GeoJSON
            data={spillPolygon}
            style={{ color: "#000", weight: 2, dashArray: "5 5", fillColor: "#1f2325", fillOpacity: 0.7 }}
          />
        )}

        {showAis &&
          aisTracks &&
          Object.entries(aisTracks).map(([vesselId, trackPoints]) => {
            const isSelected = selectedVesselId === vesselId;
            const trackColor = vesselId === "vessel_a" ? "#58d8ba" : vesselId === "vessel_b" ? "#ffdb71" : "#cdd8e2";
            return (
              <React.Fragment key={vesselId}>
                <Polyline
                  positions={trackPoints.map((pt) => [pt.latitude, pt.longitude])}
                  pathOptions={{
                    color: trackColor,
                    weight: isSelected ? 4 : 2,
                    opacity: isSelected ? 1.0 : 0.6,
                  }}
                  eventHandlers={{
                    click: () => onVesselSelect(vesselId),
                  }}
                >
                  <Popup>
                    <strong>{trackPoints[0].name}</strong><br />
                    MMSI: {trackPoints[0].mmsi}<br />
                    Type: {trackPoints[0].vessel_type}
                  </Popup>
                </Polyline>
                {trackPoints.map((pt, idx) => (
                  <CircleMarker
                    key={`${vesselId}-${idx}`}
                    center={[pt.latitude, pt.longitude]}
                    radius={isSelected ? 5 : 3}
                    pathOptions={{
                      color: trackColor,
                      fillColor: trackColor,
                      fillOpacity: 1.0,
                    }}
                    eventHandlers={{
                      click: () => onVesselSelect(vesselId),
                    }}
                  />
                ))}
              </React.Fragment>
            );
          })}
      </MapContainer>
    </div>
  );
}
