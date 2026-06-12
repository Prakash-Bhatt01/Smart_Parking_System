# Requirements Document

## Introduction

The Django Smart Parking System currently generates QR codes during payment processing and saves them as physical files to the filesystem. This approach fails on Render's free tier deployment because Render uses an ephemeral filesystem where files are lost on every restart, redeploy, or container migration, resulting in 404 errors when users attempt to view their booking QR codes.

This requirements document specifies a dynamic on-demand QR code generation solution that eliminates filesystem dependency by generating QR codes in-memory when requested, ensuring reliable operation on Render's ephemeral infrastructure while maintaining zero external costs.

## Glossary

- **QR_Generator_View**: The Django view responsible for generating and serving QR codes dynamically
- **Booking_System**: The existing Django application that manages parking slot bookings
- **Ephemeral_Filesystem**: A non-persistent storage system where files are lost on container restart
- **Payment_Processor**: The process_payment() function that confirms bookings
- **Template_Renderer**: Django templates that display booking information to users
- **Authentication_System**: Django's @login_required decorator and user authentication
- **HTTP_Cache**: Browser and HTTP-level caching mechanism controlled by Cache-Control headers

## Requirements

### Requirement 1: Dynamic QR Code Generation View

**User Story:** As a system user, I want QR codes to be generated on-demand when I request them, so that they are always available regardless of server restarts.

#### Acceptance Criteria

1. WHEN a user requests a QR code via URL pattern /qr/<booking_id>/, THEN THE QR_Generator_View SHALL generate a QR code in-memory using the qrcode library
2. WHEN generating a QR code, THEN THE QR_Generator_View SHALL include booking ID, slot number, and lot name in the QR data
3. WHEN the QR code generation completes, THEN THE QR_Generator_View SHALL return an HTTP response with content type image/png
4. WHEN returning the QR code, THEN THE QR_Generator_View SHALL use a BytesIO buffer to avoid filesystem writes
5. THE QR_Generator_View SHALL use qrcode library version 1 with error correction level L, box size 10, and border 4

### Requirement 2: User Authentication and Authorization

**User Story:** As a system administrator, I want QR code access to be restricted to authenticated users who own the booking, so that user privacy and data security are maintained.

#### Acceptance Criteria

1. WHEN an unauthenticated user requests a QR code, THEN THE Authentication_System SHALL redirect them to the login page with a return URL
2. WHEN an authenticated user requests a QR code for a booking they own, THEN THE QR_Generator_View SHALL verify ownership using the booking.user field
3. WHEN an authenticated user requests a QR code for a booking they do not own, THEN THE QR_Generator_View SHALL return HTTP 404 Not Found
4. WHEN a booking ID does not exist in the database, THEN THE QR_Generator_View SHALL return HTTP 404 Not Found
5. THE QR_Generator_View SHALL enforce authentication using Django's @login_required decorator

### Requirement 3: URL Routing Configuration

**User Story:** As a developer, I want a dedicated URL pattern for QR code generation, so that QR codes can be accessed via predictable URLs.

#### Acceptance Criteria

1. THE Booking_System SHALL define a URL pattern /qr/<int:booking_id>/ that routes to the QR_Generator_View
2. WHEN the URL pattern matches, THEN THE Booking_System SHALL pass the booking_id as an integer parameter to the view
3. THE URL pattern SHALL be named 'serve_qr_code' for use in Django template URL reversal
4. THE URL pattern SHALL validate that booking_id is an integer type before routing to the view

### Requirement 4: Payment Processing Modification

**User Story:** As a system maintainer, I want QR code generation removed from the payment process, so that payment processing is simplified and filesystem writes are eliminated.

#### Acceptance Criteria

1. WHEN processing a payment, THEN THE Payment_Processor SHALL NOT generate QR code files
2. WHEN processing a payment, THEN THE Payment_Processor SHALL NOT perform filesystem writes to the qrcodes directory
3. WHEN processing a payment, THEN THE Payment_Processor SHALL set booking status to 'confirmed'
4. WHEN processing a payment AND the qr_code field is not modified AND the save operation succeeds, THEN THE Payment_Processor SHALL save the booking record to the database
5. THE Payment_Processor SHALL remain compatible with existing bookings that have qr_code field values

### Requirement 5: Template Updates

**User Story:** As a user, I want to see QR codes displayed in my bookings list, so that I can access them for parking verification.

#### Acceptance Criteria

1. WHEN rendering the my_bookings template, THEN THE Template_Renderer SHALL use the {% url 'serve_qr_code' booking.id %} tag to generate QR code URLs
2. WHEN a booking has status 'confirmed' or 'active', THEN THE Template_Renderer SHALL display an img tag with src pointing to the QR_Generator_View
3. WHEN a booking has status other than 'confirmed' or 'active', THEN THE Template_Renderer SHALL display "N/A" text
4. WHEN rendering QR code images, THEN THE Template_Renderer SHALL apply loading="lazy" attribute for performance optimization
5. WHEN a user clicks a QR code, THEN THE Template_Renderer SHALL open the QR code in a new browser tab using target="_blank"

### Requirement 6: HTTP Caching

**User Story:** As a system administrator, I want QR code responses to be cacheable, so that server CPU usage is minimized for repeated requests.

#### Acceptance Criteria

1. WHEN returning a QR code response, THEN THE QR_Generator_View SHALL include a Cache-Control header with value "public, max-age=3600"
2. WHEN a browser receives a QR code with caching headers, THEN THE HTTP_Cache SHALL cache the image for 3600 seconds (1 hour)
3. WHEN a cached QR code is requested within the cache period, THEN THE HTTP_Cache SHALL serve the cached version without contacting the server
4. THE QR_Generator_View SHALL set the Content-Type header to "image/png" for all QR code responses

### Requirement 7: Error Handling

**User Story:** As a user, I want clear error responses when QR codes cannot be generated, so that I understand when access is denied or bookings don't exist.

#### Acceptance Criteria

1. IF a booking does not exist in the database, THEN THE QR_Generator_View SHALL return HTTP 404 Not Found
2. IF a user is not authenticated, THEN THE Authentication_System SHALL return HTTP 302 redirect to the login page
3. IF a user does not own the requested booking, THEN THE QR_Generator_View SHALL return HTTP 404 Not Found
4. IF the booking_id parameter is not a valid integer, THEN THE Booking_System SHALL return HTTP 404 Not Found
5. IF QR code generation fails due to library errors, THEN THE QR_Generator_View SHALL raise an exception that Django handles with HTTP 500

### Requirement 8: Backward Compatibility

**User Story:** As a system maintainer, I want existing bookings with qr_code field values to continue working, so that historical data remains accessible.

#### Acceptance Criteria

1. THE Booking_System SHALL retain the qr_code ImageField in the Booking model for backward compatibility
2. WHEN displaying bookings, THEN THE Template_Renderer SHALL check booking.status instead of booking.qr_code to determine QR code display
3. WHEN an old booking has a qr_code field value, THEN THE Template_Renderer SHALL display the dynamically generated QR code instead
4. THE Booking_System SHALL NOT require database migrations to remove the qr_code field
5. THE Booking_System SHALL allow the qr_code field to be blank and null

### Requirement 9: Performance Requirements

**User Story:** As a user, I want QR codes to load quickly, so that my booking information is readily accessible.

#### Acceptance Criteria

1. WHEN generating a single QR code, THEN THE QR_Generator_View SHALL complete generation within 200 milliseconds
2. WHEN a user views a page with multiple bookings, THEN THE Template_Renderer SHALL use lazy loading to defer off-screen QR code generation
3. WHEN browser cache is enabled, THEN THE HTTP_Cache SHALL serve subsequent QR code requests from cache in less than 10 milliseconds
4. THE QR_Generator_View SHALL generate QR codes as PNG images with file size less than 5 kilobytes
5. WHEN concurrent QR code requests occur, THEN THE Booking_System SHALL handle at least 10 parallel requests without performance degradation

### Requirement 10: Deployment Compatibility

**User Story:** As a system administrator, I want the QR code solution to work reliably on Render's free tier, so that the application remains cost-free and deployment-ready.

#### Acceptance Criteria

1. THE QR_Generator_View SHALL NOT write any files to the filesystem during operation
2. THE QR_Generator_View SHALL NOT depend on persistent storage for QR code availability
3. WHEN the Render container restarts, THEN THE QR_Generator_View SHALL continue serving QR codes without errors
4. WHEN the application is redeployed AND the database is available, THEN THE QR_Generator_View SHALL generate QR codes using current booking data from the database
5. IF the database is unavailable during QR code generation, THEN THE QR_Generator_View SHALL fail and return an error
6. THE Booking_System SHALL work on any hosting platform with ephemeral filesystems including Render, Heroku, and Railway
