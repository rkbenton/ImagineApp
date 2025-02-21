# Changelog for ImageApp


Changelog Summary for Recent Updates
Enhancements & Refactoring

    Introduced DataManager as a Singleton
        Centralized config and theme data handling.
        Ensures a single instance manages configuration throughout the app.

    Environment Variable Handling
        Config path (IM_IM_CONFIG_PATH) is now accessed via os.environ[NAME] instead of os.getenv().
        self.config_error is initialized before calling load_dotenv() to prevent uninitialized errors.

Error Handling & UI Improvements

    Improved Startup Error Handling
        If the config path is missing or invalid, the error is stored in DataManager instead of crashing Flask.
        The error is passed to Flask and displayed in the UI.

    Added Error Reporting via Modals
        Frontend: Errors (including startup errors) are now shown in a modal dialog instead of failing silently.
        Backend: Flask routes return structured JSON errors, including unexpected failures and file issues.

    Updated UI Components
        Boolean Fields: Replaced checkboxes with Tailwind sliding toggles.
        Help Buttons (?) now open modals for better mobile UX.
        Error Modals: Display messages when config loading or saving fails.

Logging & Debugging Enhancements

    Added structured logging using logging module
        Logs errors to the console for easier debugging.
        Catches FileNotFoundError, JSONDecodeError, and other issues gracefully.

# Initial Commit
This is a fully functional Flask + Tailwind UI prototype. It covers: 

✅ Config loading & saving
✅ Tailwind styling
✅ Interactive UI with JavaScript
✅ Basic validation & toggles