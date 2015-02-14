Build an exporter for Timeline
==============================

In Timeline an Exporter is used to export data from a timeline to a file. The Exporter transforms the
data into a format that is understood by another application such as a web browser or a spreadsheet
program.

To be able to install an Exporter into Timeline it must be built as a Plugin. That means it must
implement all the methods defined in the class PluginBase. To install the Exporter it is placed in the
directory timlinelib.plugin.plugins.

Step 1 – Inherit from PluginBase
--------------------------------

Say that we want to build an Exporter that creates a file to be used by the fictive application
EventViewer. The first thing to do is to create a module with a class definition like this:
from timelinelib.plugin.pluginbase import PluginBase
class ExportToEventViewerFile(PluginBase):
pass

Step 2 – Implement base class methods
-------------------------------------

Next step is to implement the methods defined in the PluginBase class.
from timelinelib.plugin.pluginbase import PluginBase
from timelinelib.plugin.factory import EXPORTER
class ExportToEventViewerFile(PluginBase):
def displayname(self):
return _(“Export to EventViewer...”)
def service(self):
return EXPORTER
def run(timeline, parent=None)
pass
Note that the displayname() returns a string surrounded by _(). The reason for this is to make it
possible to internationalize the text.

Step 3 – Write the implementation
---------------------------------

The implementation is written in the run() method.
This method is passed a timeline object, from which information about the timeline data can be
retrieved. The parent argument is the gui object from which the run function is called. For exporters,
this is the mainframe window.
The following timeline methods are useful for retrieving timeline data.
timeline.get_all_events() Return a list with all events in a timeline
timeline.get_containers() Return a list with all container events in a timeline
timeline.get_categories() Return a list with all categories in a timeline
Useful Event functions.
event.get_text() Returns the event title
event.get_category() Returns the category associated with the event
container.get_subevents() Returns the events associated with the container

Step 4 – Install the Exporter
-----------------------------

Put the module that contains the Exporter in the timleinelib.plugin.plugins
directory. That’s it!  Sample code::

    from timelinelib.plugin.pluginbase import PluginBase
    from timelinelib.plugin.factory import EXPORTER

    FILE_DESCRIPTION = _("Event viewer files")
    FILE_EXTENSIONS = ["txt"]
    PLUGIN_DISPLAYNAME = _("Export to EventViewer...")

    class SampleExporter(PluginBase):

        def displayname(self):
            return PLUGIN_DISPLAYNAME

        def service(self):
            return EXPORTER

        def run(self, timeline, parent=None):
            path = self._get_save_path(self.parent, FILE_DESCRIPTION, FILE_EXTENSIONS)
            if path is not None:
                result = self._transform_data(timeline)
                self._save_result_to_file(result, path)

        def _transform_data(self, timeline):
            collector = []
            for event in timeline.get_all_events():
            collector.append(self._transform_event(event))
            return "".join(collector)

        def _transform_event(self, event):
            return "%s %s\n" % (event.get_text(), event.get_time_period().get_label())
