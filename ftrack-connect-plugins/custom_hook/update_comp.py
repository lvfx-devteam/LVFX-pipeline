import os
import sys
import ftrack
import getpass
import logging


class UpdateCompMetadata(ftrack.Action):

    label = 'Update To Latest'
    identifier = 'com.ftrack.updateCompMeta'

    def getProjectFolder(self, project):
        projFolder = project.get('root')
        if projFolder == '':
            disk = ftrack.Disk(project.get('diskid'))
            rootFolder = ''
            if sys.platform == 'win32':
                rootFolder = disk.get('windows')
            elif sys.platform == 'linux2':
                rootFolder = disk.get('unix')
            projectName = project.getName()
            if projectName == 'lafras':
                projectName = 'Lafras'
            projFolder = os.path.join(rootFolder, projectName)
        return projFolder

    def getLatestCompScript(self, task):
        filename = ''
        project = ftrack.Project(task.get('showid'))
        projectFolder = self.getProjectFolder(project)
        shot = task.getParent()
        sequence = shot.getParent()
        sceneFolder = os.path.join(projectFolder, 'shots', sequence.getName(), shot.getName(), 'scene')
        taskFolder = os.path.join(sceneFolder, task.getName().lower())
        files = [f for f in os.listdir(taskFolder) if f.endswith('.nk')]

        if files:
            files.sort()
            filename = os.path.join(taskFolder, files[-1])
        return filename


    def register(self):
        '''Register discover actions on logged in user.'''
        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.discover and source.user.username={0}'.format(
                getpass.getuser()
            ),
            self.discover
        )

        ftrack.EVENT_HUB.subscribe(
            'topic=ftrack.action.launch and source.user.username={0} '
            'and data.actionIdentifier={1}'.format(
                getpass.getuser(), self.identifier
            ),
            self.launch
        )

    def discover(self, event):
        '''Return action config if triggered on a single selection.'''
        selection = event['data'].get('selection', [])

        if not selection:
            return

        entityType = selection[0]['entityType']

        if entityType == 'task':
            task = ftrack.Task(selection[0]['entityId'])
            if task.getName().lower() == 'compositing':
                return {
                    'items': [{
                        'label': self.label,
                        'actionIdentifier': self.identifier
                    }]
                }
            else:
                return

    def launch(self, event):
        """
        Called when action is executed
        """
        selection = event['data'].get('selection', [])
        task = ftrack.Task(selection[0]['entityId'])

        filename = self.getLatestCompScript(task)
        print filename
        metadata = task.getMeta()
        metadata['filename'] = filename

        task.setMeta(metadata)

        return {
                'success': True,
                'message': 'Action launched successfully.'
            }


def register(registry, **kw):
    '''Register action. Called when used as an event plugin.'''
    logger = logging.getLogger(
        'com.ftrack.updateCompMeta'
    )

    # Validate that registry is an instance of ftrack.Registry. If not,
    # assume that register is being called from a new or incompatible API and
    # return without doing anything.
    if not isinstance(registry, ftrack.Registry):
        logger.debug(
            'Not subscribing plugin as passed argument {0!r} is not an '
            'ftrack.Registry instance.'.format(registry)
        )
        return

    action = UpdateCompMetadata()
    action.register()