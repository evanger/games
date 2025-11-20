import sqlite3
import pandas as pd
import os
import sys
import time
import wx

class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(880,700))
        self.CreateStatusBar()
        self.SetStatusText("Application ready.")

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(255, 255, 255))


        # Setting up the menu.
        filemenu= wx.Menu()

        menuAbout = filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuUpdate = filemenu.Append(wx.ID_ANY,"&Update"," Update the game database")
        menuDelete = filemenu.Append(wx.ID_ANY,"&Delete"," Delete the game database")
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File")
        self.SetMenuBar(menuBar)

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.UpdateDialog, menuUpdate)
        self.Bind(wx.EVT_MENU, self.DeleteDialog, menuDelete)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)

        # Range boundaries (# player)
        self.min_val = 1
        self.max_val = 10

        # Labels for the sliders (# player)
        wx.StaticText(self.panel, label="Minimum Player Count:", pos=(40, 20))
        wx.StaticText(self.panel, label="Maximum Player Count:", pos=(40, 70))

        # Display for current range (# player)
        self.range_display = wx.StaticText(self.panel, label="", pos=(40, 130))
        self.update_range_display()

        # Slider for MIN value (# player)
        self.slider_min = wx.Slider(self.panel, value=1, minValue=self.min_val,
                                    maxValue=self.max_val, pos=(40, 40),
                                    size=(350, -1),
                                    style=wx.SL_HORIZONTAL | wx.SL_LABELS)

        # Slider for MAX value (# player)
        self.slider_max = wx.Slider(self.panel, value=4, minValue=self.min_val,
                                    maxValue=self.max_val, pos=(40, 90),
                                    size=(350, -1),
                                    style=wx.SL_HORIZONTAL | wx.SL_LABELS)

        # Bind slider events (# player)
        self.slider_min.Bind(wx.EVT_SLIDER, self.on_min_slider_change)
        self.slider_max.Bind(wx.EVT_SLIDER, self.on_max_slider_change)

        #
        #
        # Duplicate double sliders for game complexity
        # Range boundaries (wt)
        self.min_val_wt = 1
        self.max_val_wt = 5

        # Labels for the sliders (wt)
        wx.StaticText(self.panel, label="Minimum Game Weight:", pos=(460, 20))
        wx.StaticText(self.panel, label="Maximum Game Weight:", pos=(460, 70))

        # Display for current range (wt)
        self.range_display_wt = wx.StaticText(self.panel, label="", pos=(460, 130))
        self.update_range_display_wt()

        # Slider for MIN value (wt)
        self.slider_min_wt = wx.Slider(self.panel, value=1, minValue=self.min_val_wt,
                                    maxValue=self.max_val_wt, pos=(460, 40),
                                    size=(350, -1),
                                    style=wx.SL_HORIZONTAL | wx.SL_LABELS)

        # Slider for MAX value (wt)
        self.slider_max_wt = wx.Slider(self.panel, value=5, minValue=self.min_val_wt,
                                    maxValue=self.max_val_wt, pos=(460, 90),
                                    size=(350, -1),
                                    style=wx.SL_HORIZONTAL | wx.SL_LABELS)

        # Bind slider events (wt)
        self.slider_min_wt.Bind(wx.EVT_SLIDER, self.on_min_slider_change_wt)
        self.slider_max_wt.Bind(wx.EVT_SLIDER, self.on_max_slider_change_wt)

        # the combobox Control for number of games to display
        self.sampleList = ['5','10','15']
        self.default_selection = '10'
        self.lblhear = wx.StaticText(self.panel, label="Number of Results to Display", pos=(40, 205))
        self.edithear = wx.ComboBox(self.panel, pos=(205, 200), size=(95, -1), choices=self.sampleList, value=self.default_selection, style=wx.CB_DROPDOWN)
        self.Bind(wx.EVT_COMBOBOX, self.EvtComboBox, self.edithear)

        # Radio buttons for top or random
        self.radio_button_Top = wx.RadioButton(self.panel, label="Top", pos=(580, 205))
        self.radio_button_Top.SetValue(True)
        self.radio_button_Random = wx.RadioButton(self.panel, label="Random", pos=(630, 205))

        # Label for radio buttons
        wx.StaticText(self.panel, label="Order of Results", pos=(460, 205))

        # Bind an event handler to the radio button
        self.radio_button_Top.Bind(wx.EVT_RADIOBUTTON, self.on_radio_button_click)
        self.radio_button_Random.Bind(wx.EVT_RADIOBUTTON, self.on_radio_button_click)

        # Create a button for getting a new random result
        self.my_button = wx.Button(self.panel, label="New Random Set", pos=(700, 200))
        self.my_button.Show(self.radio_button_Random.GetValue())

        # Bind an event handler to the button
        self.my_button.Bind(wx.EVT_BUTTON, self.on_button_click)

        # Create a ListCtrl in report mode with specific position and size
        self.list_ctrl = wx.ListCtrl(self.panel, pos=(40, 280), size=(775, 320),
                                    style=wx.LC_REPORT | wx.BORDER_NONE)

        # Prevent the ListCtrl from expanding
        self.list_ctrl.SetMinSize((775, 320))
        self.list_ctrl.SetMaxSize((775, 320))

        # Make the header font bold
        bold_font = wx.Font(wx.NORMAL_FONT.GetPointSize(),
                            wx.DEFAULT,
                            wx.NORMAL,
                            wx.BOLD,
                            False,
                            wx.NORMAL_FONT.GetFaceName())
        header_attr = wx.ItemAttr()
        header_attr.SetFont(bold_font)
        self.list_ctrl.SetHeaderAttr(header_attr)

        # Add columns to the ListCtrl
        self.list_ctrl.InsertColumn(0, 'Game', width=320)
        self.list_ctrl.InsertColumn(1, 'Popular', width=65, format = wx.LIST_FORMAT_CENTRE)
        self.list_ctrl.InsertColumn(2, 'Year', width=65, format = wx.LIST_FORMAT_CENTRE)
        self.list_ctrl.InsertColumn(3, 'Geek Rating', width=105, format = wx.LIST_FORMAT_CENTRE)
        self.list_ctrl.InsertColumn(4, 'Play Time (min)', width=105, format = wx.LIST_FORMAT_CENTRE)
        self.list_ctrl.InsertColumn(5, 'BGG Rank', width=105, format = wx.LIST_FORMAT_CENTRE)

        DisplayGames(self)

        self.Show(True)


    def get_status_text(self, field=0):
        """Helper method to get the current status bar text for testing."""
        return self.GetStatusBar().GetStatusText(field)


    def on_button_click(self, event):
        DisplayGames(self)

    def EvtComboBox(self, event):
        num = int(event.GetString())
        DisplayGames(self)

    def on_radio_button_click(self, event):
        selected_radio = event.GetEventObject()
        self.my_button.Show(self.radio_button_Random.GetValue())
        DisplayGames(self)

    def update_range_display(self):
        """Update the text showing the current range."""
        min_v = self.slider_min.GetValue() if hasattr(self, 'slider_min') else 1
        max_v = self.slider_max.GetValue() if hasattr(self, 'slider_max') else 4
        self.range_display.SetLabel(f"Player Count Range: {min_v} to {max_v}")

    def on_min_slider_change(self, event):
        """Handle minimum slider changes."""
        min_value = self.slider_min.GetValue()
        max_value = self.slider_max.GetValue()

        # If min exceeds max, push max up
        if min_value > max_value:
            self.slider_max.SetValue(min_value)

        self.update_range_display()
        DisplayGames(self)

    def on_max_slider_change(self, event):
        """Handle maximum slider changes."""
        min_value = self.slider_min.GetValue()
        max_value = self.slider_max.GetValue()

        # If max goes below min, pull min down
        if max_value < min_value:
            self.slider_min.SetValue(max_value)

        self.update_range_display()
        DisplayGames(self)

    #
    # duplicate double sliders for game complexity
    def update_range_display_wt(self):
        """Update the text showing the current range."""
        min_v_wt = self.slider_min_wt.GetValue() if hasattr(self, 'slider_min_wt') else 1
        max_v_wt = self.slider_max_wt.GetValue() if hasattr(self, 'slider_max_wt') else 5
        self.range_display_wt.SetLabel(f"Game Weight: {min_v_wt} to {max_v_wt}")

    def on_min_slider_change_wt(self, event):
        """Handle minimum slider changes."""
        min_value_wt = self.slider_min_wt.GetValue()
        max_value_wt = self.slider_max_wt.GetValue()

        # If min exceeds max, push max up
        if min_value_wt > max_value_wt:
            self.slider_max_wt.SetValue(min_value_wt)

        self.update_range_display_wt()
        DisplayGames(self)

    def on_max_slider_change_wt(self, event):
        """Handle maximum slider changes."""
        min_value_wt = self.slider_min_wt.GetValue()
        max_value_wt = self.slider_max_wt.GetValue()

        # If max goes below min, pull min down
        if max_value_wt < min_value_wt:
            self.slider_min_wt.SetValue(max_value_wt)

        self.update_range_display_wt()
        DisplayGames(self)

    def UpdateDialog(self, event):
        dlg = wx.MessageDialog(self,
                            "To update the game database, select a 'collection.csv' file from Board Game Geek. Would you like to update the game database now?",
                            "Update Game Database",
                            wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)

        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_YES:
            self.OnUpdate()
        elif result == wx.ID_NO:
            print("User clicked No")
        elif result == wx.ID_CANCEL:
            print("User clicked Cancel")

    def DeleteDialog(self, event):
        dlg = wx.MessageDialog(self,
                            "Deleting the current game database is irreversible. After deletion, you will have to go to File > Upload to upload a new one. Would you like to delete the game database now?",
                            "Delete Game Database",
                            wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)

        result = dlg.ShowModal()
        dlg.Destroy()

        if result == wx.ID_YES:
            DeleteDatabase(self)
        elif result == wx.ID_NO:
            print("User clicked No")
        elif result == wx.ID_CANCEL:
            print("User clicked Cancel")

    def OnAbout(self,e):
        dlg = wx.MessageDialog( self, "A program to sort my game collection, written in Python",
                                "About Brent's Game Room", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()


    def OnUpdate(self):
        with wx.FileDialog(self, "Open BGG csv file", wildcard="XYZ files (*.csv)|*.csv",
                        style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            print(fileDialog.GetPath())
            UpdateDatabase(self,fileDialog.GetPath())

    def OnExit(self, event):
        self.Close(True)



def main():

    app = wx.App(False)
    frame = MainWindow(None, "Brent's Game Room")
    app.MainLoop()



def DisplayGames(app):
    # Clear existing items
    app.list_ctrl.DeleteAllItems()

    if app.radio_button_Top.GetValue():
        sql_str = "SELECT * FROM games WHERE (minplayers >= ? AND maxplayers <= ?) AND (avgweight >= ? AND avgweight <= ?) ORDER BY baverage DESC LIMIT ?"
    else:
        sql_str = "SELECT * FROM games WHERE (minplayers >= ? AND maxplayers <= ?) AND (avgweight >= ? AND avgweight <= ?) ORDER BY RANDOM() LIMIT ?"

    conn = sqlite3.connect('collection.db')
    cursor = conn.cursor()
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='games';"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        pass
    else:
        app.SetStatusText("No games database. Go to File > Update")
        return

    cursor.close()

    conn.close()
    conn = sqlite3.connect('collection.db')
    conn.set_trace_callback(app.SetStatusText)

    cursor = conn.cursor()
    cursor.execute(sql_str, (app.slider_min.GetValue(),app.slider_max.GetValue(),app.slider_min_wt.GetValue(),app.slider_max_wt.GetValue(),int(app.edithear.GetValue())))

    results = cursor.fetchall()


    # Populate the ListCtrl with data
    for i, row in enumerate(results):
        if int(row[24]) > 100000:
            p="\u2B50"
        else:
            p = ""
        app.list_ctrl.InsertItem(i, str(row[0]))
        app.list_ctrl.SetItem(i, 1, p)
        app.list_ctrl.SetItem(i, 2, str(int(row[32])))
        app.list_ctrl.SetItem(i, 3, str(round(row[20], 2)))
        app.list_ctrl.SetItem(i, 4, str(int(row[29])))
        app.list_ctrl.SetItem(i, 5, str(int(row[23])))

    cursor.close()
    conn.close()



def DeleteDatabase(app):
    conn = sqlite3.connect('collection.db')
    conn.close()
    # Check if the file exists before attempting to delete it
    if os.path.exists('collection.db'):
        try:
            os.remove('collection.db')
            app.SetStatusText("Games database successfully deleted.")
            time.sleep(2)
            DisplayGames(app)
        except OSError as e:
            app.SetStatusText(f"Error deleting game database: {e}")
    else:
        app.SetStatusText(f"Game database does not exist.")
        time.sleep(2)
        DisplayGames(app)


def UpdateDatabase(app,FilePath):
    df = pd.read_csv(FilePath)
    df.set_index('objectname')

    conn = sqlite3.connect('collection.db')

    cursor = conn.cursor()
    query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='games';"
    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        cursor.execute("SELECT COUNT(*) FROM games")
        before = cursor.fetchone()[0]
        cursor.close()
    else:
        before = 0

    cursor.close()

    df.to_sql('games', con=conn, if_exists='append', index=False)

    cursor = conn.cursor()
    cursor.execute("CREATE TABLE temp_table AS SELECT DISTINCT * FROM games")
    cursor.execute("DELETE FROM games")
    cursor.execute("INSERT INTO games SELECT * FROM temp_table")
    cursor.execute("DROP TABLE temp_table")
    cursor.close()

    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM games")
    after = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    app.SetStatusText(f"Game database updated! {after} entries. {after - before} additions")
    time.sleep(2)
    DisplayGames(app)

if __name__ == "__main__":
    main()
