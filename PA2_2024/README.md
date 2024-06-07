# SimpleScene.py

## 1. global variables

```python
    cowpos = np.zeros((4,4)) # cow position
    animStartTime=0 # animation start time
    pick = -1 # pick state
    pick_pos = [] # pick position
    currentPos=[] # current position
```


## 2. onKeyPress(window, key, scancode, action, mods)

> "if a number is pressed, alter the camera corresponding the number."

    주석으로 적혀있는 이 부분을 구현하였습니다.
    
```python    
    if key==glfw.KEY_1: 
        cameraIndex = 0;
        print( "Toggle camera %s\n"% cameraIndex );
    elif key==glfw.KEY_2:
        cameraIndex = 1;
        print( "Toggle camera %s\n"% cameraIndex ); 
    elif key==glfw.KEY_3: 
        cameraIndex = 2;
        print( "Toggle camera %s\n"% cameraIndex );
    elif key==glfw.KEY_4: 
        cameraIndex = 3;
        print( "Toggle camera %s\n"% cameraIndex );
    elif key==glfw.KEY_5: 
        cameraIndex = 4;
        print( "Toggle camera %s\n"% cameraIndex );
```

    원래는 위와 같이 구현했었는데 이걸 반복문으로 더 단축시킬 수 있을 것 같아서 아래와 같이 변경하였습니다.

```python
    for i in range(5): # 0 ~ 4
        if key==glfw.KEY_1+i: # KEY_1 ~ KEY_5
            cameraIndex = i;
            print( "Toggle camera %s\n"% cameraIndex );
            break;
```

## 3. spline(t, p0, p1, p2, p3)

```python
    def spline(t, p0, p1, p2, p3) :
        return (0.5*((2*p1)*np.power(t,0) + (-p0 + p2)*np.power(t,1) + 
        (2*p0 - 5*p1 + 4*p2 - p3)*np.power(t,2) + (-p0 + 3*p1 - 3*p2 + p3)*np.power(t,3)))
```

    spline 함수는 강의 자료에 있는 Catmull-Rom spline을 이용하여 구현하였습니다.

## 4. Locating_Cow(pos)

```python
    def Locating_Cow(pos):
        global cowpos
        peak = np.arcsin(pos[1])
        
        if np.arctan2(pos[2], pos[0]) < 0: 
            peak = -np.arcsin(pos[1])

        # Rx : peak 방향으로 회전
        Rx = np.array([[1., 0., 0.],
                    [0., np.cos(peak), -np.sin(peak)],
                    [0., np.sin(peak), np.cos(peak)]])
        # Ry : pos 방향으로 회전
        Ry = np.array([[np.cos(np.arctan2(pos[2], pos[0])), 0., np.sin(np.arctan2(pos[2], pos[0]))],
                    [0., 1., 0.],
                    [-np.sin(np.arctan2(pos[2], pos[0])), 0., np.cos(np.arctan2(pos[2], pos[0]))]])
        # Rz : identity matrix
        Rz = np.array([[1., 0, 0.],
                    [0., 1., 0.],
                    [0., 0., 1.]])

        cowpos[:3, :3] = (Ry@Rx@Rz).T
```

    display()에서 보면 Locating_Cow()의 인자가 direction 즉, 방향벡터입니다.
    그렇기 때문에 소의 local 축에서 y축을 위쪽을 향하는 벡터로 하기 위해 pos[1]을 peak로 설정해줍니다.
    그런데 만약, np.arctan2(pos[2], pos[0])이 0보다 작은 경우 (-)부호를 붙여 주어 보정합니다.
    Rx, Ry, Rz를 설정해준 뒤, 소의 위치를 Rx, Ry, Rz의 행렬곱으로 표현합니다.

## 5. display()

```python
    if not (pick<0 or pick>=6) : # pick_pos에 저장된 위치로 cow를 이동
        for i in pick_pos : 
            drawCow(i, True)
    elif pick == 6 : # spline을 이용해 cow를 이동
        cpos = np.zeros((4, 4)) # cow의 위치
        elapsed_t = glfw.get_time() - animStartTime
        t = elapsed_t % 6 # 0~6 사이의 값으로 변환

        if (elapsed_t < 18) :
            aTime=float(elapsed_t)-int(elapsed_t) # 0~1 사이의 값으로 변환
            
            for i in range(6):
                if i <= t and t < i + 1:
                    cpos = spline(aTime, pick_pos[(i-1) % 6], pick_pos[i % 6], pick_pos[(i+1) % 6], pick_pos[(i+2) % 6])
                    break
        else:
            cow2wld = cowpos
            pick = -1
            pick_pos.clear()
            glFlush()
            return
        
        direction = normalize(getTranslation(cpos) - getTranslation(cowpos))
        Locating_Cow(direction) # cow의 방향 설정
        setTranslation(cowpos, getTranslation(cpos)) # cow의 위치 설정 
        drawCow(cowpos, False)

    if pick != 6 : # spline을 이용해 cow를 이동하지 않을 때
        drawCow(cow2wld, cursorOnCowBoundingBox);
```

    display 함수의 경우 소를 화면에 띄우는 역할을 하는 함수입니다.
    먼저 if not (pick<0 or pick>=6) 의 경우 pick이 0과 6사이에 있기 때문에 유효한 pick이므로 그대로 drawCow()로 소를 그려줍니다.
    그 다음 pick이 6인 경우, 이 경우는 위에서 구현한 spline으로 소를 이동시킵니다.
    get_time()과 animStartTime으로 경과 시간 (elapsed_t)를 구해서 t와 aTime을 구한 뒤 t가 0과 6 사이일 때 spline 함수로 소의 위치를 구해줍니다.
    여기서 p0, p1, p2, p3는 pick_pos[(i-k) % 6]의 형태로 인자로 넘겨주었는데, 그 이유는 spline interpolation으로 주어진 4개의 점을 매끄럽게 만들어주기 위해서 입니다. 
    만약 경과 시간이 18초를 넘겼다면 초기화해줍니다.

    방향벡터는 getTranslation으로 현재 위치에서 소의 위치를 빼서 구해주었고
    새로 만든 Locating_Cow 함수로 소의 방향을 설정한 뒤 setTranslation으로 위치를 찍어서
    소를 그려주었습니다.

## 6. onMouseButton(window, button, state, mods)

```python
    elif state == GLFW_UP and isDrag!=0:
        isDrag=H_DRAG;
        print( "Left mouse up\n");
        if cursorOnCowBoundingBox :
            if -1<=pick and pick<6 :
                pick+=1
            if 0<pick and pick<7:
                pick_pos.append(cow2wld.copy())
                if pick == 6 :
                    animStartTime = glfw.get_time()
                    cowpos = pick_pos[0].copy()
                    isDrag = 0
```

    수직으로 dragging을 할 경우 왼쪽 마우스를 떼었을 때 pick을 하도록 해주는 함수입니다.
    만약 이 code가 없다면 bounding box에 마우스를 올려놓고 클릭한 뒤 드래그를 하면 위아래 이동은 가능하지만,
    클릭을 떼었을 때 소의 위치가 기록되지 않아 수직 이동을 하지 않게 됩니다.
    
## 7. onMouseDrag

```python
    if isDrag: 
        print( "in drag mode %d\n"% isDrag);
        if  isDrag==V_DRAG:
            # vertical dragging
            # TODO:
            # create a dragging plane perpendicular to the ray direction, 
            # and test intersection with the screen ray.
            print('vdrag')

            ray=screenCoordToRay(window,x,y)
            pp=pickInfo; 
            p=Plane(ray.direction,currentPos)
            c=ray.intersectsPlane(p) 
            
            print(pp.cowPickPosition, currentPos)
            print(pp.cowPickConfiguration, cow2wld)
            
            currentPos[1]=ray.getPoint(c[1])[1] # p + td -> (x, y) : y

            T=np.eye(4) 
            setTranslation(T, currentPos-pp.cowPickPosition)
            cow2wld=T@pp.cowPickConfiguration;
```

> Hint: read carefully the following block to implement vertical dragging.

이 힌트를 보고 아래 horizontal dragging에 대한 code를 참고해서 구현했습니다.
거의 모든 code가 동일하지만, isDrag==V_DRAG와 else part의 가장 큰 차이점은 "cursorOnCowBoundingBox"에 있습니다.

수평 이동의 경우 한 번 클릭한 이후 다음에 한 번 더 클릭을 하게 되었을 때 소의 위치가 찍히게 되는 반면
수직 이동의 경우는 마우스 커서를 소의 bounding box에 둔 상태로 drag를 해서 이동을 한 뒤 커서를 놓았을 때 소의 위치가 찍히게 됩니다.

따라서 조건문 (if cursorOnCowBoundingBox) 없이 구현을 하였고, horizontal dragging의 경우 y축을 normal vector로 갖기 때문에
p=Plane(np,array((0,1,0)), cursorPos)로 y축을 normal vector로 설정했다면 vertical dragging의 경우는 ray direction과 perpendicular하기 때문에
p=Plane(ray.direction, currentPos)로 ray direction을 normal vector로 하는 평면에 대해 이동을 하도록 구하였습니다.

그렇기 때문에 currentPos도 vertical dragging의 경우 y 좌표만 움직이기 때문에
currentPos[1]=ray.getPoint(c[1])[1]로 p+t*d로 이동한 점의 y좌표만 update해서 반영하도록 하였습니다.

# 결과

![스크린샷 2024-06-07 201128](https://github.com/Hyunjoon83/ComputerGraphics/assets/141709404/2aa4ec97-ae3a-4256-a2f9-d8e4e1089e5e)
