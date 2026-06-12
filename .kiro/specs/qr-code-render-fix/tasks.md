# Implementation Plan: QR Code Render Production Fix

## Overview

This implementation plan fixes the QR code 404 errors on Render production by implementing dynamic on-demand QR code generation. The solution eliminates filesystem dependency by generating QR codes in-memory when requested, ensuring reliable operation on Render's ephemeral infrastructure with zero external costs.

The current system generates QR codes during payment processing and saves them as files to `media/qrcodes/`, which fails on Render because the free tier uses an ephemeral filesystem (files are lost on every restart/redeploy). The new approach creates a dedicated Django view that generates QR codes dynamically, serving them directly as HTTP responses without any filesystem writes.

## Implementation Approach

**Key Changes:**
1. Create new `serve_qr_code` view that generates QR codes in-memory
2. Add URL pattern `/qr/<booking_id>/` to route QR requests
3. Remove QR generation logic from `process_payment` view
4. Update templates to use dynamic QR URLs instead of file URLs
5. No database migrations required (backward compatible)

**Benefits:**
- 100% free solution (no external services)
- Works on Render's ephemeral filesystem
- Survives container restarts and redeployments
- Zero maintenance overhead
- Estimated implementation time: ~45 minutes

## Tasks

- [ ] 1. Create dynamic QR code generation view
  - Add new `serve_qr_code` function to `parking/views.py`
  - Implement `@login_required` decorator for authentication
  - Retrieve booking by ID and verify ownership with `user=request.user`
  - Generate QR code in-memory using qrcode library with booking data
  - Return QR as HTTP response with `content_type='image/png'`
  - Add `Cache-Control: public, max-age=3600` header for browser caching
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 6.1, 6.2, 6.3, 6.4_

- [ ] 2. Add URL routing for QR code view
  - Update `parking/urls.py` to add URL pattern: `path('qr/<int:booking_id>/', views.serve_qr_code, name='serve_qr_code')`
  - Verify URL pattern validates booking_id as integer type
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 3. Remove QR generation from payment processing
  - Modify `process_payment` function in `parking/views.py`
  - Remove all QR code generation logic (lines creating qr object, image, buffer)
  - Remove `booking.qr_code.save()` call
  - Keep booking status update to 'confirmed' and save
  - Keep success message and redirect logic
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 4. Checkpoint - Verify backend implementation
  - Run development server locally
  - Test that serve_qr_code view is accessible
  - Verify URL routing works for `/qr/<id>/`
  - Check that process_payment no longer generates files
  - Ask the user if questions arise

- [ ] 5. Update my_bookings.html template
  - Locate QR code display section in `templates/my_bookings.html`
  - Replace `{% if booking.qr_code %}` condition with `{% if booking.status == 'confirmed' or booking.status == 'active' %}`
  - Change `src="{{ booking.qr_code.url }}"` to `src="{% url 'serve_qr_code' booking.id %}"`
  - Change `href="{{ booking.qr_code.url }}"` to `href="{% url 'serve_qr_code' booking.id %}"`
  - Add `loading="lazy"` attribute to img tag for performance
  - Update else clause to show "N/A" for non-confirmed bookings
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.1, 8.2, 8.3_

- [ ] 6. Update booking_success.html template (if exists)
  - Search `templates/booking_success.html` for QR code references
  - If QR code is displayed, update using same pattern as my_bookings.html
  - Replace `booking.qr_code.url` with `{% url 'serve_qr_code' booking.id %}`
  - Add `loading="lazy"` attribute to img tag
  - If file doesn't exist or no QR code displayed, skip this task
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 7. Search and update any other templates with QR references
  - Search all templates in `templates/` directory for `booking.qr_code`
  - Check `booking_detail.html`, admin templates, email templates
  - Update any found references using the same pattern
  - Replace file URL references with dynamic view URLs
  - If no other references found, mark this task complete
  - _Requirements: 5.1, 8.3_

- [ ] 8. Checkpoint - Test complete implementation locally
  - Run `python manage.py runserver`
  - Login as a user and create a new booking
  - Complete payment and verify redirect to success page
  - Navigate to "My Bookings" page
  - Verify QR codes display correctly for confirmed bookings
  - Verify QR codes show "N/A" for pending/cancelled bookings
  - Click on QR code image - verify it opens in new tab as PNG
  - Right-click QR code - verify "Save Image As" option works
  - Check browser DevTools Network tab - verify QR requests return 200 status
  - Verify QR codes load reasonably fast (<200ms per request)
  - Test with mobile QR scanner app - verify QR data is readable
  - Ask the user if questions arise

- [ ]* 9. Write unit tests for serve_qr_code view
  - Create test in `parking/tests.py` for authenticated user accessing own booking QR
  - Test that QR code returns HTTP 200 with content-type image/png
  - Test that unauthenticated user is redirected to login (HTTP 302)
  - Test that user cannot access another user's booking QR (HTTP 404)
  - Test that non-existent booking returns HTTP 404
  - Test that invalid booking_id returns HTTP 404
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 7.1, 7.2, 7.3, 7.4_

- [ ]* 10. Write integration tests for complete QR workflow
  - Test complete flow: create booking → payment → view QR code
  - Test that QR code is accessible immediately after payment
  - Test that QR code persists across multiple page views
  - Test browser caching by checking Cache-Control header
  - Test lazy loading attribute is present in template
  - _Requirements: 1.1, 5.4, 6.1, 6.2, 9.1, 9.3_

- [ ] 11. Prepare for deployment
  - Commit all changes with message: "Fix: Dynamic QR code generation for Render ephemeral filesystem"
  - Verify no new dependencies added to requirements.txt
  - Review changes: `git diff` to ensure only intended files modified
  - Verify `.gitignore` includes `media/qrcodes/` to prevent tracking old QR files
  - Push changes to GitHub repository
  - _Requirements: 10.1, 10.2_

- [ ] 12. Deploy to Render and verify production
  - Push changes to main branch (triggers auto-deploy on Render)
  - Monitor Render deployment logs for successful build
  - Wait for deployment to complete
  - Visit production URL and login
  - Create a test booking on production
  - Complete payment and verify QR code displays
  - Check browser DevTools - verify no 404 errors
  - Open QR code in new tab - verify it loads as PNG
  - Test QR code with mobile scanner - verify data is readable
  - **Critical test:** Trigger Render container restart (redeploy or wait for inactivity timeout)
  - After restart, access same booking QR URL again
  - **Success criteria:** QR code still displays correctly (not 404)
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [ ] 13. Verify performance and caching in production
  - Check Render logs for any errors related to QR generation
  - Use browser DevTools Network tab to measure QR generation time
  - Verify QR codes load in less than 200ms on production
  - Verify Cache-Control header is present in response
  - Reload page - verify subsequent QR requests use browser cache (from cache status)
  - Test with multiple bookings (5-10) - verify all QR codes load successfully
  - Monitor Render CPU usage - ensure it remains within free tier limits
  - _Requirements: 6.1, 6.2, 6.3, 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ] 14. Final verification and cleanup
  - Test complete user journey: login → book slot → payment → view bookings → access QR
  - Verify QR codes work for both car and bike bookings
  - Test with different browsers (Chrome, Firefox, Safari if available)
  - Test on mobile device - verify QR codes display and are scannable
  - Verify existing old bookings (with qr_code field values) display dynamic QR codes
  - Verify cancelled bookings show "N/A" instead of QR code
  - Update project documentation (README, RENDER_DEPLOYMENT_GUIDE.md) with QR fix details
  - Optional: Remove old QR code files from git tracking: `git rm -r --cached media/qrcodes/`
  - Optional: Add `media/qrcodes/` to `.gitignore` if not already present
  - _Requirements: All_

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP delivery
- No database migrations required - the `qr_code` ImageField remains in the model for backward compatibility but is not used
- Total estimated implementation time: 45 minutes (including local testing)
- Deployment verification time: 15 minutes (including container restart test)
- The solution is stateless and requires zero maintenance
- QR generation uses existing qrcode library - no new dependencies needed
- Each task references specific requirements from the requirements document for traceability
- Checkpoints ensure incremental validation and provide opportunities for user feedback
- The implementation is fully reversible via git revert if any issues arise
- Performance optimization includes HTTP caching (1 hour) and lazy loading
- Security is enforced through @login_required decorator and user ownership verification

## Rollback Plan

If issues arise during deployment:

1. **Quick rollback via git:**
   ```bash
   git revert HEAD
   git push origin main
   ```

2. **No database rollback needed** - no migrations were created

3. **No data loss risk** - only view/template logic changed

4. **After rollback:**
   - QR codes will show 404 again (expected - original issue)
   - All other functionality remains intact
   - Can retry fix after troubleshooting

## Success Criteria

- [ ] QR codes display correctly on Render production
- [ ] No 404 errors after container restarts
- [ ] QR codes survive redeployments
- [ ] Booking workflow completes end-to-end
- [ ] QR codes are scannable with mobile apps
- [ ] Solution remains 100% free
- [ ] No external dependencies or API keys required
- [ ] Page load performance is acceptable (<200ms per QR)
- [ ] Browser caching reduces subsequent load times
- [ ] All tests pass (unit + integration, if written)
