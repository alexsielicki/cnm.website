from cStringIO import StringIO
from icalendar import Calendar

from plone.i18n.normalizer import idnormalizer

def create_events_from_ics(self):
    filename = '/home/bschreiber/Downloads/adecalendar.ics'
    cal = Calendar.from_ical(open(filename,'rb').read())
    calendar_items = cal.walk()
    pwflow = self.portal_workflow
    events_folder = self.events
    buff = StringIO()
    num_events_created = 0
    for cal_item in calendar_items:
        if cal_item.name == 'VEVENT':
            title = cal_item['SUMMARY'].title()
            description = cal_item['DESCRIPTION'].title()
            organizer = cal_item['ORGANIZER'].title()
            location = cal_item['LOCATION'].title()
            start = cal_item['DTSTART'].dt
            end = cal_item['DTEND'].dt
            ev_id = idnormalizer.normalize(title)
            id_extension = 1
            keep_trying = True
            while keep_trying:
                try:
                    event_id = events_folder.invokeFactory('Event', id=ev_id, title=title)
                    ev_obj = events_folder[event_id]
                    ev_obj.setStartDate(start)
                    ev_obj.setEndDate(end)
                    ev_obj.setLocation(location)
                    ev_obj.setText(description)
                    keep_trying = False
                    num_events_created +=1
                    buff.write('Created event with id '+ev_id+'\n')
                except Exception, e: 
                    ev_id = ev_id[:len(ev_id)-2]+'-'+str(id_extension)
                    id_extension += 1
    buff.write('\n====\n'+str(num_events_created)+' events created...')
    buff.seek(0)
    return buff.read()
