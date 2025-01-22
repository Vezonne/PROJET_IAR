# Genetic Algorithm

## Parameters

- 3 sensors per side
- 3 links per sensor
- 9 int per sensor [0, 99]:
  1. `init_offset`
  2. `gradient1`
  3. `threshold1`
  4. `gradient2`
  5. `threshold2`
  6. `gradient3`
  7. `slope_modulation`
  8. `offset_modulation`
  9. `battery_number`

- 9 link outputs are summed, passed through a sigmoid [-3, 3] and scaled to [-10, 10] per side

## Scaling

- offset and thresholds: scaled to [-100, 100] ($m = \dfrac{200}{99} \cdot n - 100$)
- gradients: scaled to [$-\dfrac{\pi}{2}$, $\dfrac{\pi}{2}$] and passed to the tangent ($m = \tan(\dfrac{\pi}{99} \cdot n - \dfrac{\pi}{2})$)
- `offset_modulation`: scaled to [-1, 1] ($m = \dfrac{2}{99} \cdot n - 1$)
- `slope_modulation`: scaled to [0, 1] ($m = \dfrac{1}{99} \cdot n$)
