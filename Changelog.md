# Changelog for ImagineApp

## v0.1.1 - Latest Updates

### Enhancements & Refactoring
- **Improved Theme & Styles Handling**
  - Styles dropdown now updates **dynamically** when the theme changes. (*ac329cd, f011343*)  
  - Moved **active-theme → theme-disk-name mapping** from the UI layer to the business logic layer for better separation of concerns. (*9dd51aa*)  

- **DataManager Improvements**
  - Added **quality-of-life (QOL) enhancements** in `DataManager.py` to streamline data handling. (*48e82c2*)  
  - Introduced **structured logging** in `DataManager.py` for better debugging. (*107697a*)  
  - Moved **business logic** related to data management from Flask routes to `DataManager.py`. (*d1744e5*)  

### Error Handling & UI Enhancements
- **Better Error Handling**
  - Improved error handling throughout the application, ensuring more graceful failures and logging. (*7e6f069*)  

- **User Experience (UX) Improvements**
  - Added **help buttons (`?`)** for key fields to provide guidance. (*566e091*)  

### Other Updates
- **Documentation & Requirements**
  - Cleaned up and updated `README.md`. (*bcf2129, 421256b*)  
  - Updated `requirements.txt` with necessary dependencies. (*8462860*)  

- **Versioning**
  - Added **version `v0.1.0`** to `Changelog.md` to track major changes. (*cb23d90*)  

---

## v0.1.0 - Initial Release
- Introduced **ImagineApp** with a Flask + Tailwind UI.  
- Implemented **DataManager as a Singleton** for managing configuration and theme data.  
- Added **error reporting via modals** to improve UI feedback.  
- Replaced checkboxes with **Tailwind sliding toggles** for boolean fields.  
- **Implemented structured logging** for debugging and troubleshooting.  
