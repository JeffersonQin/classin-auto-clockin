#include <windows.h>
#include <iostream>

using namespace std;

BOOL CALLBACK EnumWindowsProcMy(HWND hwnd,LPARAM lParam)
{
    DWORD lpdwProcessId;
    GetWindowThreadProcessId(hwnd, &lpdwProcessId);
    
	RECT rect;
	GetWindowRect(hwnd, &rect);
	
	TCHAR className[1024];
	GetClassName(hwnd, className, sizeof(className));
	
	TCHAR windowName[2048];
	GetWindowText(hwnd, windowName, sizeof(windowName));
	
	if (windowName) {
		cout << "-----------" << endl;
		cout << "HWND: " << hwnd << endl;
		cout << "RECT: " << rect.left << " " << rect.right << " " << rect.top << " " << rect.bottom << endl;
		cout << "Class: " << className << endl;
		cout << "Title: " << windowName << endl;
		cout << "PID: " << lpdwProcessId << endl;	
	}
	return TRUE;
}

int main() {
	EnumWindows(EnumWindowsProcMy, NULL);
	return 0;
}

