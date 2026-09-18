export interface TelemetryData {
  engine_id: string;
  timestamp: number;
  engine_hours: number;
  rpm: number;
  engine_temp: number;
  cylinder_head_temp: number;
  oil_temp: number;
  oil_pressure: number;
  fuel_flow: number;
  fuel_pressure: number;
  manifold_pressure: number;
  exhaust_gas_temp: number;
  vibration: number;
  throttle: number;
  ambient_temp: number;
  altitude: number;
  engine_load: number;
  battery_voltage: number;
}

export interface DerivedFeatures {
  temperature_rate: number;
  vibration_rate: number;
  oil_pressure_rate: number;
  rpm_change: number;
  fuel_flow_change: number;
  temperature_vibration_ratio: number;
  rolling_temperature_mean: number;
  rolling_vibration_mean: number;
  rolling_oil_pressure_mean: number;
  is_glitch_filtered: boolean;
}

export interface QualityMetrics {
  quality_rpm: number;
  quality_temp: number;
  quality_oil: number;
  quality_vib: number;
  total_packets: number;
  glitches_filtered: number;
}

export interface ExpectedPhysics {
  expected_rpm: number;
  expected_engine_temp: number;
  expected_cylinder_head_temp: number;
  expected_oil_temp: number;
  expected_oil_pressure: number;
  expected_fuel_flow: number;
  expected_fuel_pressure: number;
  expected_manifold_pressure: number;
  expected_exhaust_gas_temp: number;
  expected_vibration: number;
  expected_load: number;
}

export interface Residuals {
  residual_engine_temp: number;
  residual_oil_temp: number;
  residual_oil_pressure: number;
  residual_fuel_flow: number;
  residual_manifold_pressure: number;
  residual_exhaust_gas_temp: number;
  residual_vibration: number;
  z_scores: {
    temp: number;
    oil_press: number;
    vib: number;
    fuel: number;
    egt: number;
  };
  composite_residual_norm: number;
}

export interface XAIContribution {
  feature: string;
  label: string;
  weight_pct: number;
}

export interface MLPrediction {
  is_anomaly: boolean;
  anomaly_intensity: number;
  predicted_fault: string;
  confidence: number;
  rul: {
    rul_hours: number;
    initial_rul: number;
    degradation_index: number;
    degradation_velocity: number;
    degradation_rate_pct: number;
    confidence_pct: number;
    confidence_interval: {
      lower: number;
      upper: number;
    };
    stress_multiplier: number;
    component_wear_pct: {
      thermal_barrier: number;
      crank_bearings: number;
      lubrication_system: number;
      fuel_injection: number;
    };
    label: string;
    disclaimer: string;
  };
  explainability: {
    predicted_fault: string;
    confidence_pct: number;
    contributions: XAIContribution[];
    diagnostic_narrative: string[];
    root_cause_summary: string;
  };
}

export interface HealthState {
  health_score: number;
  status: 'HEALTHY' | 'DEGRADING' | 'CRITICAL';
  status_color: string;
  penalties: {
    physics_penalty: number;
    ml_penalty: number;
    fault_penalty: number;
    rate_stress_penalty: number;
  };
}

export interface Recommendation {
  fault_class: string;
  title: string;
  recommended_action: string;
  urgency: 'INFO' | 'WARNING' | 'CRITICAL';
  disclaimer: string;
}

export interface CANBusState {
  status: string;
  bus_type: string;
  baud_rate: string;
  packets_per_sec: number;
  latency_ms: number;
  packet_loss_pct: number;
  bus_load_pct: number;
  total_frames: number;
  error_frames: number;
  security: {
    communication: string;
    encryption: string;
    authentication: string;
  };
}

export interface MissionState {
  mission_id: string;
  scenario: string;
  scenario_name: string;
  state: 'IDLE' | 'RUNNING' | 'PAUSED' | 'STOPPED';
  elapsed_time: number;
  peak_temp: number;
  max_vibration: number;
  min_oil_pressure: number;
  faults_observed: string[];
  final_health: number;
  final_rul: number;
}

export interface TimelineStage {
  index: number;
  name: string;
  start_time: number;
  duration: number;
  is_active: boolean;
  is_completed: boolean;
}

export interface DemoState {
  demo_active: boolean;
  is_paused?: boolean;
  current_time_sec?: number;
  total_duration_sec?: number;
  total_progress_pct?: number;
  step_index: number;
  total_steps: number;
  step_name: string;
  step_description: string;
  step_progress_pct: number;
  step_elapsed: number;
  step_duration: number;
  timeline?: TimelineStage[];
}

export interface AlertItem {
  id: number;
  timestamp: number;
  time_str: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  title: string;
  message: string;
  recommended_action: string;
  confidence: number;
  acknowledged: boolean;
}

export interface FullEngineState {
  timestamp: number;
  time_str: string;
  engine_id: string;
  engine_hours: number;
  mission: MissionState;
  demo: DemoState;
  telemetry: TelemetryData;
  derived: DerivedFeatures;
  quality: QualityMetrics;
  expected_physics: ExpectedPhysics;
  residuals: Residuals;
  ml_prediction: MLPrediction;
  health: HealthState;
  recommendation: Recommendation;
  can_bus: CANBusState;
  fault_injection: {
    active_fault: string;
    severity_name: string;
    current_severity: number;
    target_severity: number;
    ramp_progress: number;
  };
  active_alerts: AlertItem[];
}

export interface HistoricalPoint {
  time: string;
  timestamp: number;
  rpm: number;
  engine_temp: number;
  oil_pressure: number;
  oil_temp: number;
  vibration: number;
  fuel_flow: number;
  exhaust_gas_temp: number;
  expected_temp: number;
  expected_oil_press: number;
  expected_vib: number;
  health_score: number;
  rul_hours: number;
}
