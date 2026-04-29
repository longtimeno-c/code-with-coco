/**
 * ─────────────────────────────────────────────────────────────
 *   gcal-declutterer
 *   automatically grays out past events in your google calendar
 * ─────────────────────────────────────────────────────────────
 *
 *   what it does:
 *   every hour, this script scans your google calendars, finds
 *   events that have already ended, and moves them to a "past
 *   events" calendar set to gray. past stuff fades into the
 *   background. upcoming stuff stays bright.
 *
 *   setup:
 *   see the README at
 *   github.com/cocohernandez/code-with-coco/tree/main/gcal-declutterer
 *
 * ─────────────────────────────────────────────────────────────
 *   made by coco hernandez ♡
 *
 *   tiktok      @cocopuffffffffs
 *   instagram   @cocohdzz
 *   github      github.com/cocohernandez
 *
 *   part of my series "code with coco"! random little projects i build
 *   for fun. you don't have to be a CS person to follow along.
 * ─────────────────────────────────────────────────────────────
 */

function movePastEventsToLightGrayCalendar() {
  const today = new Date();

  // TODO: replace with your gray calendar
  const lightGrayCalendarId = "REPLACE_WITH_GRAY_CALENDAR_ID@group.calendar.google.com";  
  const lightGrayCalendar = CalendarApp.getCalendarById(lightGrayCalendarId);

  // TOOD: replace with your colorful calendar IDs
  const calendarIds = [
    "REPLACE_WITH_EACH_CALENDAR_ID@gmail.com",                  // Personal
    "REPLACE_WITH_EACH_CALENDAR_ID@group.calendar.google.com",  // Classes
    "REPLACE_WITH_EACH_CALENDAR_ID@group.calendar.google.com",  // Clubs & Orgs
    "REPLACE_WITH_EACH_CALENDAR_ID@group.calendar.google.com",  // Exams/Finals
    "REPLACE_WITH_EACH_CALENDAR_ID@group.calendar.google.com",  // Gym
    "REPLACE_WITH_EACH_CALENDAR_ID@group.calendar.google.com",  // Office Hours
    "REPLACE_WITH_EACH_CALENDAR_ID@group.calendar.google.com",  // Stanford
    "REPLACE_WITH_EACH_CALENDAR_ID@group.calendar.google.com",  // TikTok
    "REPLACE_WITH_EACH_CALENDAR_ID@group.calendar.google.com"   // Meals
  ];

  calendarIds.forEach(calendarId => {
    try {
      const calendar = CalendarApp.getCalendarById(calendarId);
      const oneWeekAgo = new Date();
      oneWeekAgo.setDate(today.getDate() - 7); 

      Logger.log(`Checking events for calendar ID: ${calendarId}`);

      const events = calendar.getEvents(oneWeekAgo, today); 

      if (events.length === 0) {
        Logger.log(`No events found for calendar: ${calendarId}`);
      }

      events.forEach(event => {
        if (event.getEndTime() < today) { 
          Logger.log(`Moving event: ${event.getTitle()} to light gray calendar`);

          let guests = [];
          try {
            guests = event.getGuestList().map(guest => guest.getEmail());
          } catch (guestError) {
            Logger.log(`No valid guest list for event: ${event.getTitle()} - ${guestError.message}`);
          }

          const newEvent = lightGrayCalendar.createEvent(
            event.getTitle(),
            event.getStartTime(),
            event.getEndTime(),
            {
              description: event.getDescription(),
              location: event.getLocation()
            }
          );

          if (guests.length > 0) {
            guests.forEach(guestEmail => {
              try {
                newEvent.addGuest(guestEmail);
              } catch (guestAddError) {
                Logger.log(`Failed to add guest: ${guestEmail} to event: ${event.getTitle()} - ${guestAddError.message}`);
              }
            });
          }

          event.deleteEvent();
        }
      });
    } catch (error) {
      Logger.log(`Error processing calendar with ID: ${calendarId} - ${error.message}`);
    }
  });
}
