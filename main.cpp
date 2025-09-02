#include <windows.h>
#include <scrnsave.h>
#include <commctrl.h>
#include <math.h>
#include <time.h>
#include <vector>
#include <string>
#include <cstdio>

// Configuration
int numCircles = DEFAULT_NUM_CIRCLES;
float speedMultiplier = DEFAULT_SPEED_MULTIPLIER;
float fadeSpeed = DEFAULT_FADE_SPEED;
#define DARKER_FACTOR 0.5f
#define LIGHTER_FACTOR 1.5f
#define OUTER_WIDTH 6
#define INNER_WIDTH 2
#define MOVE_AMOUNT 1.0f
#define FILL_CIRCLES false
#define EXIT_DELAY 2.0f
#define MIN_MOUSE_DISTANCE 5.0f

// Registry keys
#define REG_KEY "Software\\BouncingSaver"
#define REG_NUM_CIRCLES "NumCircles"
#define REG_SPEED "SpeedMultiplier"
#define REG_FADE "FadeSpeed"

// Dialog control IDs
#define IDC_NUM_CIRCLES 1001
#define IDC_SPEED 1002
#define IDC_FADE 1003
#define IDC_STATIC1 1004
#define IDC_STATIC2 1005
#define IDC_STATIC3 1006

// Color list
COLORREF colorList[] = {
    RGB(255, 0, 0),     // RED
    RGB(255, 165, 0),   // ORANGE
    RGB(255, 255, 0),   // YELLOW
    RGB(0, 128, 0),     // GREEN
    RGB(0, 0, 255),     // BLUE
    RGB(128, 0, 128),   // PURPLE
    RGB(255, 192, 203), // PINK
    RGB(0, 255, 255),   // CYAN
    RGB(0, 255, 255),   // AQUA
    RGB(255, 0, 255),   // MAGENTA
    RGB(255, 215, 0),   // GOLD
    RGB(0, 255, 0),     // LIME
    RGB(64, 224, 208),  // TURQUOISE
    RGB(255, 255, 255)  // WHITE
};
const int numColors = sizeof(colorList) / sizeof(colorList[0]);

void LoadSettings() {
    HKEY hKey;
    if (RegOpenKeyEx(HKEY_CURRENT_USER, REG_KEY, 0, KEY_READ, &hKey) == ERROR_SUCCESS) {
        DWORD value, size = sizeof(DWORD);
        if (RegQueryValueEx(hKey, REG_NUM_CIRCLES, NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
            numCircles = value;
        }
        if (RegQueryValueEx(hKey, REG_SPEED, NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
            speedMultiplier = *(float*)&value; // Note: This is a hack; better to store as string
        }
        if (RegQueryValueEx(hKey, REG_FADE, NULL, NULL, (LPBYTE)&value, &size) == ERROR_SUCCESS) {
            fadeSpeed = *(float*)&value;
        }
        RegCloseKey(hKey);
    }
}

void SaveSettings() {
    HKEY hKey;
    if (RegCreateKeyEx(HKEY_CURRENT_USER, REG_KEY, 0, NULL, REG_OPTION_NON_VOLATILE, KEY_WRITE, NULL, &hKey, NULL) == ERROR_SUCCESS) {
        RegSetValueEx(hKey, REG_NUM_CIRCLES, 0, REG_DWORD, (LPBYTE)&numCircles, sizeof(DWORD));
        RegSetValueEx(hKey, REG_SPEED, 0, REG_DWORD, (LPBYTE)&speedMultiplier, sizeof(float));
        RegSetValueEx(hKey, REG_FADE, 0, REG_DWORD, (LPBYTE)&fadeSpeed, sizeof(float));
        RegCloseKey(hKey);
    }
}
    float x, y, dx, dy, radius;
    int colorIndex, nextColorIndex;
    float fadeT;
};

std::vector<Circle> circles;
int screenWidth, screenHeight;
float startTime;
bool mouseMoved = false;

COLORREF LerpColor(COLORREF c1, COLORREF c2, float t) {
    int r = (int)(GetRValue(c1) + (GetRValue(c2) - GetRValue(c1)) * t);
    int g = (int)(GetGValue(c1) + (GetGValue(c2) - GetGValue(c1)) * t);
    int b = (int)(GetBValue(c1) + (GetBValue(c2) - GetBValue(c1)) * t);
    return RGB(r, g, b);
}

void InitCircles(HWND hwnd) {
    RECT rect;
    GetClientRect(hwnd, &rect);
    screenWidth = rect.right;
    screenHeight = rect.bottom;

    circles.clear();
    srand((unsigned int)time(NULL));

    for (int i = 0; i < numCircles; ++i) {
        float radius = (float)(rand() % 41 + 35); // 35-75
        float angle = (float)(rand() / (float)RAND_MAX * 2 * 3.14159);
        float speed = MOVE_AMOUNT;
        float dx = cosf(angle) * speed;
        float dy = sinf(angle) * speed;
        float x = (float)(rand() / (float)RAND_MAX * (screenWidth - 2 * radius) + radius);
        float y = (float)(rand() / (float)RAND_MAX * (screenHeight - 2 * radius) + radius);
        int colorIndex = i % numColors;
        int nextColorIndex = (colorIndex + 1) % numColors;

        Circle c = { x, y, dx, dy, radius, colorIndex, nextColorIndex, 0.0f };
        circles.push_back(c);
    }
}

void UpdateCircles(float deltaTime) {
    for (auto& c : circles) {
        c.x += c.dx * speedMultiplier * deltaTime;
        c.y += c.dy * speedMultiplier * deltaTime;

        // Bounce
        if (c.x - c.radius <= 0) {
            c.x = c.radius;
            c.dx *= -1;
        } else if (c.x + c.radius >= screenWidth) {
            c.x = screenWidth - c.radius;
            c.dx *= -1;
        }
        if (c.y - c.radius <= 0) {
            c.y = c.radius;
            c.dy *= -1;
        } else if (c.y + c.radius >= screenHeight) {
            c.y = screenHeight - c.radius;
            c.dy *= -1;
        }

        // Fade
        c.fadeT += fadeSpeed * deltaTime;
        if (c.fadeT >= 1.0f) {
            c.fadeT = 0.0f;
            c.colorIndex = c.nextColorIndex;
            c.nextColorIndex = (c.nextColorIndex + 1) % numColors;
        }
    }

    // Collisions
    for (size_t i = 0; i < circles.size(); ++i) {
        for (size_t j = i + 1; j < circles.size(); ++j) {
            Circle& c1 = circles[i];
            Circle& c2 = circles[j];
            float dx = c1.x - c2.x;
            float dy = c1.y - c2.y;
            float distSq = dx * dx + dy * dy;
            float minDistSq = (c1.radius + c2.radius) * (c1.radius + c2.radius);
            if (distSq < minDistSq) {
                // Swap velocities
                std::swap(c1.dx, c2.dx);
                std::swap(c1.dy, c2.dy);
                // Separate
                float dist = sqrtf(distSq);
                if (dist > 0) {
                    float overlap = (c1.radius + c2.radius) - dist;
                    float angle = atan2f(dy, dx);
                    c1.x += cosf(angle) * (overlap / 2);
                    c1.y += sinf(angle) * (overlap / 2);
                    c2.x -= cosf(angle) * (overlap / 2);
                    c2.y -= sinf(angle) * (overlap / 2);
                }
            }
        }
    }
}

void DrawCircles(HDC hdc) {
    for (const auto& c : circles) {
        COLORREF color = LerpColor(colorList[c.colorIndex], colorList[c.nextColorIndex], c.fadeT);
        if (FILL_CIRCLES) {
            // Filled circle (not implemented, use Ellipse or something)
        } else {
            // Beveled outline
            COLORREF darker = RGB((int)(GetRValue(color) * DARKER_FACTOR),
                                  (int)(GetGValue(color) * DARKER_FACTOR),
                                  (int)(GetBValue(color) * DARKER_FACTOR));
            COLORREF lighter = RGB(min(255, (int)(GetRValue(color) * LIGHTER_FACTOR)),
                                   min(255, (int)(GetGValue(color) * LIGHTER_FACTOR)),
                                   min(255, (int)(GetBValue(color) * LIGHTER_FACTOR)));

            // Outer
            HPEN hPen = CreatePen(PS_SOLID, OUTER_WIDTH, darker);
            SelectObject(hdc, hPen);
            Ellipse(hdc, (int)(c.x - c.radius), (int)(c.y - c.radius), (int)(c.x + c.radius), (int)(c.y + c.radius));
            DeleteObject(hPen);

            // Inner
            hPen = CreatePen(PS_SOLID, INNER_WIDTH, lighter);
            SelectObject(hdc, hPen);
            Ellipse(hdc, (int)(c.x - c.radius), (int)(c.y - c.radius), (int)(c.x + c.radius), (int)(c.y + c.radius));
            DeleteObject(hPen);
        }
    }
}

LRESULT WINAPI ScreenSaverProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static DWORD lastTime = 0;
    static POINT lastMousePos = { 0, 0 };

    switch (msg) {
    case WM_CREATE:
        LoadSettings();
        InitCircles(hwnd);
        SetTimer(hwnd, 1, 16, NULL); // ~60 FPS
        startTime = (float)GetTickCount() / 1000.0f;
        GetCursorPos(&lastMousePos);
        break;

    case WM_TIMER:
        if (wParam == 1) {
            DWORD currentTime = GetTickCount();
            float deltaTime = (currentTime - lastTime) / 1000.0f;
            if (lastTime == 0) deltaTime = 1.0f / 60.0f;
            lastTime = currentTime;
            UpdateCircles(deltaTime);
            InvalidateRect(hwnd, NULL, TRUE);
        }
        break;

    case WM_PAINT: {
        PAINTSTRUCT ps;
        HDC hdc = BeginPaint(hwnd, &ps);
        DrawCircles(hdc);
        EndPaint(hwnd, &ps);
        break;
    }

    case WM_MOUSEMOVE: {
        POINT pt;
        GetCursorPos(&pt);
        int dx = pt.x - lastMousePos.x;
        int dy = pt.y - lastMousePos.y;
        float currentTime = (float)GetTickCount() / 1000.0f;
        if (currentTime - startTime > EXIT_DELAY && (abs(dx) > MIN_MOUSE_DISTANCE || abs(dy) > MIN_MOUSE_DISTANCE)) {
            PostQuitMessage(0);
        }
        lastMousePos = pt;
        break;
    }

    case WM_KEYDOWN:
    case WM_LBUTTONDOWN:
    case WM_RBUTTONDOWN:
    case WM_MBUTTONDOWN:
        PostQuitMessage(0);
        break;

    case WM_DESTROY:
        KillTimer(hwnd, 1);
        break;
    }

    return DefScreenSaverProc(hwnd, msg, wParam, lParam);
}

BOOL WINAPI ScreenSaverConfigureDialog(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) {
    static HWND hNumCircles, hSpeed, hFade;
    char buffer[256];

    switch (msg) {
    case WM_INITDIALOG:
        LoadSettings();
        SetWindowPos(hwnd, NULL, 0, 0, 220, 150, SWP_NOMOVE | SWP_NOZORDER);
        // Create controls
        CreateWindow("STATIC", "Number of Circles:", WS_CHILD | WS_VISIBLE, 10, 10, 120, 20, hwnd, (HMENU)IDC_STATIC1, NULL, NULL);
        hNumCircles = CreateWindow("EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER | ES_NUMBER, 140, 10, 50, 20, hwnd, (HMENU)IDC_NUM_CIRCLES, NULL, NULL);
        sprintf(buffer, "%d", numCircles);
        SetWindowText(hNumCircles, buffer);

        CreateWindow("STATIC", "Speed Multiplier:", WS_CHILD | WS_VISIBLE, 10, 40, 120, 20, hwnd, (HMENU)IDC_STATIC2, NULL, NULL);
        hSpeed = CreateWindow("EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER, 140, 40, 50, 20, hwnd, (HMENU)IDC_SPEED, NULL, NULL);
        sprintf(buffer, "%.2f", speedMultiplier);
        SetWindowText(hSpeed, buffer);

        CreateWindow("STATIC", "Fade Speed:", WS_CHILD | WS_VISIBLE, 10, 70, 120, 20, hwnd, (HMENU)IDC_STATIC3, NULL, NULL);
        hFade = CreateWindow("EDIT", "", WS_CHILD | WS_VISIBLE | WS_BORDER, 140, 70, 50, 20, hwnd, (HMENU)IDC_FADE, NULL, NULL);
        sprintf(buffer, "%.4f", fadeSpeed);
        SetWindowText(hFade, buffer);

        CreateWindow("BUTTON", "OK", WS_CHILD | WS_VISIBLE | BS_DEFPUSHBUTTON, 50, 100, 50, 25, hwnd, (HMENU)IDOK, NULL, NULL);
        CreateWindow("BUTTON", "Cancel", WS_CHILD | WS_VISIBLE, 120, 100, 50, 25, hwnd, (HMENU)IDCANCEL, NULL, NULL);
        return TRUE;

    case WM_COMMAND:
        if (LOWORD(wParam) == IDOK) {
            GetWindowText(hNumCircles, buffer, sizeof(buffer));
            numCircles = atoi(buffer);
            GetWindowText(hSpeed, buffer, sizeof(buffer));
            speedMultiplier = (float)atof(buffer);
            GetWindowText(hFade, buffer, sizeof(buffer));
            fadeSpeed = (float)atof(buffer);
            SaveSettings();
            EndDialog(hwnd, TRUE);
        } else if (LOWORD(wParam) == IDCANCEL) {
            EndDialog(hwnd, FALSE);
        }
        break;

    case WM_CLOSE:
        EndDialog(hwnd, FALSE);
        break;
    }
    return FALSE;
}

BOOL WINAPI RegisterDialogClasses(HANDLE hInst) {
    return TRUE;
}
