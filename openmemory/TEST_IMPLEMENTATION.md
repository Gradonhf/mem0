# Testing the Msty.ai Implementation

## Overview
This document provides a step-by-step guide to test the Msty.ai implementation and the new scrollable dashboard functionality.

## Prerequisites
- OpenMemory application running (`make up`)
- Browser access to `http://localhost:3000`

## Test Steps

### 1. Verify Msty.ai App Integration

#### Test the Apps Page
1. Navigate to `http://localhost:3000/apps`
2. Verify that Msty.ai appears in the apps list
3. Check that Msty.ai has the correct icon (indigo-colored SVG)
4. Verify the app name displays as "Msty.ai"

#### Test the Dashboard Install Component
1. Navigate to `http://localhost:3000` (dashboard)
2. Look for the "Install OpenMemory" section
3. Verify that Msty.ai appears in the horizontal tab list
4. Check that Msty.ai has the correct indigo color gradient when selected
5. Click on the Msty.ai tab
6. Verify the installation command appears:
   ```
   npx @openmemory/install local http://localhost:8765/mcp/msty/sse/{user} --client msty
   ```
7. Test the copy button functionality

### 2. Test Scrollable Dashboard

#### Test Horizontal Scrolling
1. On the dashboard, locate the application tabs list
2. If you have a narrow screen or many apps, verify that:
   - The list scrolls horizontally
   - A subtle scrollbar appears at the bottom
   - A fade indicator appears on the right edge
   - All apps are accessible by scrolling

#### Test Responsive Design
1. Resize your browser window to different widths
2. Verify that the app list adapts properly
3. Check that scrolling works on mobile devices (if testing mobile)

### 3. Test Custom App Creation

#### Create a Custom App
1. Navigate to `http://localhost:3000/apps`
2. Click "Add New App" button
3. Fill in the form:
   - Name: `test-custom-app`
   - Description: `Test custom application`
4. Submit the form
5. Verify the app appears in the grid with:
   - Generic edit icon
   - Formatted name: "Test Custom App"
   - Proper styling

#### Test App Name Validation
1. Try creating an app with invalid name: `Test App` (uppercase)
2. Verify error message appears
3. Try creating an app with spaces: `test app`
4. Verify error message appears
5. Try creating duplicate app name
6. Verify error message appears

### 4. Test API Endpoints

#### Test Create App API
```bash
curl -X POST "http://localhost:8765/api/v1/apps/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "api-test-app",
    "description": "App created via API",
    "metadata": {}
  }'
```

Expected response:
```json
{
  "id": "uuid-here",
  "name": "api-test-app",
  "description": "App created via API",
  "is_active": true,
  "total_memories_created": 0,
  "total_memories_accessed": 0
}
```

#### Test List Apps API
```bash
curl "http://localhost:8765/api/v1/apps/"
```

Verify that Msty.ai and any custom apps appear in the response.

### 5. Visual Verification

#### Check Icons and Styling
1. Verify Msty.ai icon appears correctly in all locations:
   - Apps page grid
   - Dashboard stats
   - Memory cards
   - Access logs
2. Verify custom apps show generic edit icon
3. Check that color gradients work properly for all apps

#### Check Responsive Behavior
1. Test on different screen sizes
2. Verify scrollable behavior works on mobile
3. Check that all interactive elements are accessible

## Expected Results

### ✅ Success Criteria
- Msty.ai appears in all app lists with correct branding
- Dashboard app list scrolls horizontally when needed
- Custom apps can be created and display properly
- All API endpoints work correctly
- UI is responsive and accessible
- Error handling works for invalid inputs

### ❌ Common Issues to Check
- Msty.ai icon not loading (check SVG file path)
- Scrollable list not working (check CSS classes)
- API errors (check backend logs)
- Styling issues (check Tailwind classes)

## Troubleshooting

### If Msty.ai doesn't appear:
1. Check browser console for errors
2. Verify the SVG file exists at `ui/public/images/msty.svg`
3. Check that the constants are properly updated

### If scrolling doesn't work:
1. Check browser console for CSS errors
2. Verify the container has proper overflow settings
3. Test on different browsers

### If API calls fail:
1. Check backend logs: `make logs`
2. Verify the API server is running
3. Check environment variables

## Performance Notes
- The scrollable list should be smooth and responsive
- No performance degradation with many apps
- Copy functionality should work instantly
- API responses should be fast (< 100ms)

## Browser Compatibility
Test on:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile) 