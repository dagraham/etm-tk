# etmtk Notes

iCalendar sync

    Option for relative path "ics_txt" in data dir. If present, ics_txt.ics will automatically be created and updated with iCalendar export of ics_txt.txt and vice versa. 
    
    Check modification times. If ics is more recent then import to txt, else if txt is more recent, then export to ics.
     
    If either import or export occurs sync the last acess/modified times:
        now = datetime.datetime.now()
        epoch = datetime.datetime(1970, 1, 1, 0, 0, 0, 0)
        seconds = (mow - epoch).total_seconds()
        os.utime(ics_sync.txt, times=(seconds, seconds))
        os.utime(ics_sync.ics, times=(seconds, seconds))
    
google:
etmTk
dauntless-bay-618

Client Id: 841985535824-pov6qjeu2sfh0d0vfp3isbvteo9hb476.apps.googleusercontent.com

Email: 841985535824-pov6qjeu2sfh0d0vfp3isbvteo9hb476@developer.gserviceaccount.com

Client secret: {"web":{"auth_uri":"https://accounts.google.com/o/oauth2/auth","client_secret":"P2lInJBd3IavE8HjCVFAwuZI","token_uri":"https://accounts.google.com/o/oauth2/token","client_email":"841985535824-pov6qjeu2sfh0d0vfp3isbvteo9hb476@developer.gserviceaccount.com","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/841985535824-pov6qjeu2sfh0d0vfp3isbvteo9hb476@developer.gserviceaccount.com","client_id":"841985535824-pov6qjeu2sfh0d0vfp3isbvteo9hb476.apps.googleusercontent.com","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs"}}

Calendar ID: 0q3kblsrfoi35frjon6lt5ndbg@group.calendar.google.com

123456789|123456789|123456789|123456789|123456789|123456789|123456789|123456789|


File

    + Make report
    + Change history
    - Choose active calendars
    Export active calendars...

+ View

    Agenda
    ...
    ---
    Choose active calendars
    Apply filter
    Set outline depth

+ Item
    Copy
    ...

Tools
    - set outline depth
    - Make report
    - Change history

Help

## makeReport

    menu:



    ----------------------------------------------------------------
    | Menu | | X | | Search                            | | > | | ? |
    -------- --- ---------------------------------------------------
     print
     save report as
     export CSV
     email
     -------
     save changes to list



    ----------------------------------------------------------------
    | combobox                                   | | Ok | | Cancel |
    ----------------------------------------------------------------


## Menus

Save Cmd F (find), Cmd C (copy), Cmd V (paste), Cmd G (search forward),
Shift Cmd G (search backwards), Shift Cmd M (stop timer)::

    Menubar
        File
            Data file ...                  Shift-Ctrl-D
            ----
            etmtk.cfg                      Shift-Ctrl-E
            completions.cfg                Shift-Ctrl-C
            reports.cfg                    Shift-Ctrl-R
            scratchpad                     Shift-Ctrl-S
            ----
            Export to iCal                 Shift-Ctrl-X
            ----
            Quit
        Commands
            Jump to date                     Ctrl-J
            Set outline depth                Ctrl-O
            Choose active calendars
            ----
            Show busy periods                Ctrl-B
            Make report                      Ctrl-M
            ----
            Display yearly calendar          Ctrl-Y
            Open date calculator             Ctrl-L
            ----
            Change history                   Ctrl-H
        Help
            Search
            Help                               F1
            About                              F2
            Check for update                   F3
    Toolbar
        View
            Agenda                           Ctrl-A
            Schedule                         Ctrl-S
            Paths                            Ctrl-P
            Keywords                         Ctrl-K
            Tags                             Ctrl-T
        Add
            Item                             Ctrl-N
            Timer                            Ctrl-I
        Use
            Copy                             Ctrl-C
            Delete                           Ctrl-D
            Edit                             Ctrl-E
            Finish                           Ctrl-F
            Reschedule                       Ctrl-R
            Open link                        Ctrl-G

