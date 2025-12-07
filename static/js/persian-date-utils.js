/**
 * Persian Date Utilities for JavaScript
 * Converts Gregorian dates to Persian (Shamsi) calendar format
 */

class PersianDateUtils {
    /**
     * Convert Gregorian date to Persian date string
     * @param {Date|string} date - Date object or date string
     * @param {string} format - Format type: 'date', 'datetime', 'time', 'pretty'
     * @returns {string} Persian formatted date string
     */
    static formatPersianDate(date, format = 'date') {
        if (!date) return '';
        
        const dateObj = new Date(date);
        if (isNaN(dateObj.getTime())) return '';
        
        try {
            switch (format) {
                case 'date':
                    return dateObj.toLocaleDateString('fa-IR', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit'
                    });
                case 'datetime':
                    return dateObj.toLocaleString('fa-IR', {
                        year: 'numeric',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                case 'time':
                    return dateObj.toLocaleTimeString('fa-IR', {
                        hour: '2-digit',
                        minute: '2-digit'
                    });
                case 'pretty':
                    return dateObj.toLocaleDateString('fa-IR', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    });
                default:
                    return dateObj.toLocaleDateString('fa-IR');
            }
        } catch (error) {
            console.warn('Error formatting Persian date:', error);
            return dateObj.toLocaleDateString('fa-IR');
        }
    }
    
    /**
     * Format date for display in tables and lists
     * @param {Date|string} date - Date object or date string
     * @returns {string} Formatted Persian date
     */
    static formatForDisplay(date) {
        return this.formatPersianDate(date, 'date');
    }
    
    /**
     * Format datetime for display in tables and lists
     * @param {Date|string} date - Date object or date string
     * @returns {string} Formatted Persian datetime
     */
    static formatDateTimeForDisplay(date) {
        return this.formatPersianDate(date, 'datetime');
    }
    
    /**
     * Format date in pretty format for user-friendly display
     * @param {Date|string} date - Date object or date string
     * @returns {string} Pretty formatted Persian date
     */
    static formatPretty(date) {
        return this.formatPersianDate(date, 'pretty');
    }
    
    /**
     * Get relative time in Persian (e.g., "۲ ساعت پیش")
     * @param {Date|string} date - Date object or date string
     * @returns {string} Relative time in Persian
     */
    static getRelativeTime(date) {
        if (!date) return '';
        
        const dateObj = new Date(date);
        if (isNaN(dateObj.getTime())) return '';
        
        const now = new Date();
        const diffMs = now - dateObj;
        const diffSeconds = Math.floor(diffMs / 1000);
        const diffMinutes = Math.floor(diffSeconds / 60);
        const diffHours = Math.floor(diffMinutes / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffSeconds < 60) {
            return 'همین الان';
        } else if (diffMinutes < 60) {
            return `${diffMinutes} دقیقه پیش`;
        } else if (diffHours < 24) {
            return `${diffHours} ساعت پیش`;
        } else if (diffDays < 7) {
            return `${diffDays} روز پیش`;
        } else {
            return this.formatPersianDate(date, 'date');
        }
    }
    
    /**
     * Convert Persian date string to Gregorian date
     * @param {string} persianDate - Persian date string (YYYY/MM/DD)
     * @returns {Date|null} Gregorian date object or null if invalid
     */
    static persianToGregorian(persianDate) {
        if (!persianDate) return null;
        
        try {
            // This is a simplified conversion - for production use, consider using a proper library
            const parts = persianDate.split('/');
            if (parts.length !== 3) return null;
            
            const year = parseInt(parts[0]);
            const month = parseInt(parts[1]);
            const day = parseInt(parts[2]);
            
            // Basic validation
            if (year < 1300 || year > 1500 || month < 1 || month > 12 || day < 1 || day > 31) {
                return null;
            }
            
            // Simple approximation - for accurate conversion, use a proper Persian calendar library
            const gregorianYear = year + 621;
            const gregorianMonth = month - 1; // JavaScript months are 0-based
            const gregorianDay = day;
            
            return new Date(gregorianYear, gregorianMonth, gregorianDay);
        } catch (error) {
            console.warn('Error converting Persian date to Gregorian:', error);
            return null;
        }
    }
    
    /**
     * Validate if a date string is a valid Persian date
     * @param {string} dateString - Date string to validate
     * @returns {boolean} True if valid Persian date
     */
    static isValidPersianDate(dateString) {
        if (!dateString) return false;
        
        const date = this.persianToGregorian(dateString);
        return date !== null && !isNaN(date.getTime());
    }
    
    /**
     * Get current Persian date
     * @returns {string} Current date in Persian format
     */
    static getCurrentPersianDate() {
        return this.formatPersianDate(new Date(), 'date');
    }
    
    /**
     * Get current Persian datetime
     * @returns {string} Current datetime in Persian format
     */
    static getCurrentPersianDateTime() {
        return this.formatPersianDate(new Date(), 'datetime');
    }
}

// Make it available globally
window.PersianDateUtils = PersianDateUtils;

// Also provide shorter aliases for common use
window.formatPersianDate = PersianDateUtils.formatPersianDate.bind(PersianDateUtils);
window.formatPersianDateTime = PersianDateUtils.formatDateTimeForDisplay.bind(PersianDateUtils);
window.formatPersianPretty = PersianDateUtils.formatPretty.bind(PersianDateUtils);
window.getPersianRelativeTime = PersianDateUtils.getRelativeTime.bind(PersianDateUtils);
