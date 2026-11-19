# Energy and battery-life equations

Use SI units consistently. The script accepts current in mA, voltage in V and timestamps in seconds.

## Instantaneous electrical power

\[
P(t) = U(t) I(t)
\]

With voltage in volts and current in milliamps, power is in milliwatts.

## Energy over a measurement window

\[
E = \int_{t_0}^{t_1} U(t) I(t)\,dt
\]

For sampled data, the script uses trapezoidal integration:

\[
E \approx \sum_{i=0}^{N-2}
\frac{P_i + P_{i+1}}{2}(t_{i+1}-t_i)
\]

When power is in mW and time is in seconds, divide the result by 3600 to obtain mWh. Multiply mWh by 3.6 to obtain joules.

## Average current

\[
I_{avg} = \frac{1}{T}\int_{t_0}^{t_1} I(t)\,dt
\]

The script calculates this from trapezoidal integration of the current samples.

## Charge per cycle

For a periodic scenario with period \(T_c\):

\[
Q_{cycle} = I_{avg} T_c
\]

If current is in mA and period in seconds, divide by 3600 to obtain mAh per cycle.

## Energy per cycle

\[
E_{cycle} = P_{avg} T_c
\]

If power is in mW and period is in seconds, the result is mJ per cycle.

## Idealized battery autonomy

\[
L_{ideal}(h) = \frac{C_{battery}(mAh)}{I_{avg}(mA)}
\]

This assumes the full rated capacity is usable and the average current remains constant.

## Limitations

- Battery capacity depends on discharge rate, temperature, age, chemistry and cutoff voltage.
- Regulator efficiency and quiescent current are not necessarily constant across load.
- The nRF52 DK PCA10040 is not a production battery-powered PCB; board-level leakage and debug circuitry must be isolated or separately accounted for.
- Measurement bandwidth and sample rate must capture short wake-up spikes. Undersampling can miss peaks and bias integrated energy.
- Current range changes, shunt burden voltage, calibration and instrument noise affect results.
- The autonomy equation does not include self-discharge, radio activity, battery derating, burst load limitations or application-specific maintenance events.
- Do not infer the nRF52832 silicon sleep-current specification from a DK-level current measurement.

## Phase-specific current

When the CSV `phase` labels are present, the analysis script also integrates contiguous intervals whose endpoint samples share the same label (for example `idle` or `active`). An interval spanning two different labels is reported as `TRANSITION` rather than assigned arbitrarily. High sample rate and accurate phase annotation are required for short active events.

The script also reports the maximum sampled current as a simple peak indicator. This is not a guaranteed true peak: the instrument's sampling bandwidth and rate may miss a narrow transient.
