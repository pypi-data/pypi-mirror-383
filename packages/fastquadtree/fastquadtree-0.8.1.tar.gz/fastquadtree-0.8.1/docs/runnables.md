
# Runnable Examples

## 1. Interactive demo  
- Add and delete boids with mouse clicks
- Visualize KNN and range queries

```bash
pip install -r interactive/requirements.txt
python interactive/interactive_v2.py
```

![Interactive_V2_Screenshot](https://raw.githubusercontent.com/Elan456/fastquadtree/main/assets/interactive_v2_screenshot.png)

## 1.5 Interactive Demo with Rectangles
- Similar to the above demo, but uses rectangles instead of points
- If the rectangles intersect at all with the query area, they will be highlighted in red

```bash
pip install -r interactive/requirements.txt
python interactive/interactive_v2_rect.py
```

![Interactive_V2_Rect_Screenshot](https://raw.githubusercontent.com/Elan456/fastquadtree/main/assets/interactive_v2_rect_screenshot.png)

## 2. Ball Pit  
- Spawn balls in a pit with physics-based collisions
- Easily switch between brute force and quadtree collision detection to see the performance difference

```bash
pip install -r interactive/requirements.txt
python interactive/ball_pit.py
```

![Ballpit_Demo_Screenshot](https://raw.githubusercontent.com/Elan456/fastquadtree/main/assets/ballpit.png)