# LeetCode 1610 — Maximum Number of Visible Points

**Problem:**
Given a list of points on a 2D plane, an integer angle, and your location, return the maximum number of points that are visible from your location within any viewing angle of that size. Points at your location are always visible.

---

## Step-by-step Intuition

1. **Points at Your Location:**
   - Any point that coincides with your location is always visible, regardless of the viewing angle.

2. **Compute Angles:**
   - For all other points, compute the angle (in degrees or radians) from your location to each point using `atan2`.
   - Store these angles in a list.

3. **Sort and Duplicate Angles:**
   - Sort the list of angles.
   - To handle the circular nature (0° and 360° are the same), duplicate the list by adding 360° (or 2π radians) to each angle and appending it to the end.

4. **Sliding Window:**
   - Use a sliding window to find the maximum number of points within any window of size `angle`.
   - For each angle, count how many angles fall within `[current_angle, current_angle + angle]`.

5. **Add Points at Your Location:**
   - The answer is the maximum window size plus the number of points at your location.

---

## Solution (Python)

```python
import math

# Step-by-step Intuition:
# 1. Points at Your Location:
#    - Any point that coincides with your location is always visible, regardless of the viewing angle.
# 2. Compute Angles:
#    - For all other points, compute the angle (in degrees) from your location to each point using atan2.
#    - Store these angles in a list.
# 3. Sort and Duplicate Angles:
#    - Sort the list of angles.
#    - To handle the circular nature (0° and 360° are the same), duplicate the list by adding 360° to each angle and appending it to the end.
# 4. Sliding Window:
#    - Use a sliding window to find the maximum number of points within any window of size 'angle'.
#    - For each angle, count how many angles fall within [current_angle, current_angle + angle].
# 5. Add Points at Your Location:
#    - The answer is the maximum window size plus the number of points at your location.
#
# Summary:
# - We normalize all points into angle representation from the location as the origin (0,0).
# - For a given viewing angle (e.g., 30 degrees), we use a sliding window for every [currAngle, currAngle + angle] and check how many points fall within each window.
# - This efficiently finds the maximum number of visible points from the location.


    same = 0
    angles = []
    x0, y0 = location
    for x, y in points:
        # 1. Points at Your Location
        if x == x0 and y == y0:
            same += 1
        else:
            # 2. Compute Angles using atan2
            ang = math.degrees(math.atan2(y - y0, x - x0))
            if ang < 0:
                # atan2 returns angles in [-180, 180]; add 360 to negative angles to normalize to [0, 360) degrees, -45 degrees is 315 degrees in standard position
                ang += 360
            angles.append(ang)
    # 3. Sort and Duplicate Angles
    angles.sort()
    n = len(angles)
    # Duplicate the angles to handle wrap-around (circular window)
    # Example: If angles are [350, 355, 5, 10] and angle=20,
    # a window from 350 to 10 should include 350, 355, 5, 10 (crosses 0°).
    # By duplicating as [350, 355, 5, 10, 710, 715, 365, 370],
    # the sliding window can count points that wrap around 360°.
    angles += [a + 360 for a in angles]
    max_cnt = 0
    left = 0
    # 4. Sliding Window
    # For each angle, count how many points fall within [angles[left], angles[right]] <= angle
    # Duplicated angles allow the window to cross the 360°/0° boundary seamlessly
    for right in range(len(angles)):
        # Move left pointer to maintain window size <= angle
        while angles[right] - angles[left] > angle:
            left += 1
        max_cnt = max(max_cnt, right - left + 1)
    # 5. Add Points at Your Location
    return max_cnt + same

```

## Complexity Analysis
- **Time Complexity:** $O(n \log n)$ — Sorting the angles dominates.
- **Space Complexity:** $O(n)$ — For storing angles.

---

## Key Points
- Use `atan2` to compute angles from your location to each point.
- Handle wrap-around by duplicating the angle list.
- Sliding window efficiently finds the maximum number of visible points.
- Always add the count of points at your location to the result.

---

## Related Problems
- LeetCode 149: Max Points on a Line
- LeetCode 1610: Maximum Number of Visible Points (this problem)
