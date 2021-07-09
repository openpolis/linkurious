__version__ = '0.1.3'


from typing import Optional, List, Any
import tortilla


class LinkuriousException(Exception):
    """Exception generated while connecting or working with the Linkurious class"""
    pass


class Linkurious(object):
    """The main Linkurious class, representing a connection to the Linkurious remote host.

    It's a wrapper class around the low-level API calls, that uses tortilla in order to
    communicate with the REST API.

    Whenever the class is instantiated with username/password or username/apikey,
    the authentication is performed (or initialized), so that all subsequent calls
    will work, if the user has the right privileges.

        from linkurious_api import Linkurious
        l = Linkurious(
            host='https://linkurious.openpolis.io', username='pippo@openpolis.it', password='straw-H401-bliss'
        )
        sources = l.dataSources()
    """
    _wrapper = None
    authenticated = False

    def __init__(
        self,
        host: str, username: str = None, password: Optional[str] = None, apikey: Optional[str] = None,
        debug: bool = False,
    ):
        self._wrapper = tortilla.wrap(f"{host}/api", debug=debug)

        if username:
            self.authenticate(username, password=password, apikey=apikey)

    def authenticate(self, username: str, password: Optional[str] = None, apikey: Optional[str] = None):
        """Authentication method.

        Will use a proper login, exploiting session cookie, if password is passed.
        Will add an auth header if passkey is passed.

        Can be called in order to authenticate after instantiation.

            from linkurious_api import Linkurious
            l = Linkurious(
                host='https://linkurious.openpolis.io'
            )
            l.authenticate(username='pippo@openpolis.it', password='straw-H401-bliss')
            sources = l.dataSources()
        """
        if username and password:
            res = self._wrapper.auth.login.post(
                data={'usernameOrEmail': username, 'password': password}
            )
            if 'email' in res and res.email == username:
                self.authenticated = True
            else:
                raise LinkuriousException(f"could not authenticate {res.reason}")
            return
        if username and apikey:
            raise LinkuriousException("apikey authentication not yet implemented")

        raise LinkuriousException(f"could not authenticate without password or apikey")

    def get_wrapper(self):
        """Helper method that return the internal tortilla wrapper"""
        return self._wrapper

    def status(self):
        """Return the status response

        GET /api/status

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Linkurious-getStatus
        """
        return self.get_wrapper().status.get()

    def version(self):
        """Return the version response

        GET /api/version

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Linkurious-getVersion
        """
        return self.get_wrapper().version.get()

    def get_custom_files(self, root: Optional[str] = None, extensions: Optional[str] = None):
        """Returns the list of custom files for the Linkurious instance.

        GET /api/customFiles

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Linkurious-getCustomFiles
        """
        return self.get_wrapper().customFiles.get(params={'root': root, 'extensions': extensions})

    def get_sources_status(self, with_styles: bool = False, with_captions: bool = False):
        """Get the status of all data-sources

        GET /api/dataSources

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-DataSource-getDataSources
        """
        # boolean true must be transformed into 1, to be  understood by the linkkurious API
        if with_styles:
            with_styles = 1
        if with_captions:
            with_captions = 1
        return self.get_wrapper().dataSources.get(params={'with_styles': with_styles, 'with_captions': with_captions})

    def get_sources_info(self):
        """Get the admin info of all the data-sources

        GET /api/admin/sources

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-DataSource-getDataSourcesAdminInfo
        """
        return self.get_wrapper().admin.sources.get()

    def get_config(self, source_index: int = 0):
        """Get the configuration for the sourceIndex source

        GET /api/config

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Config-getConfiguration
        """
        return self.get_wrapper().get('config', params={'sourceIndex': source_index})

    def update_config(
        self, source_index: int = 0,
        path: Optional[str] = None,
        configuration_value: Optional[Any] = None,
        reset: bool = False
    ):
        """Update part of the configuration specified by path, for the sourceIndex source

        POST /api/config
        """
        data = {
            'sourceIndex': source_index,
            'reset': reset
        }
        if path:
            data['path'] = path
        if configuration_value:
            data['configuration'] = configuration_value

        return self.get_wrapper().post(
            'config',
            data=data
        )

    def get_applications(self):
        """Return the list of API applications

        GET /api/admin/applications

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Application-getApplications
        """
        return self.get_wrapper().admin.applications.get()

    def create_application(self, name: str, groups: List, rights: List, enabled: bool = True):
        """Create a new API application

        POST /api/admin/applications

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Application-createApplication
        """
        return self.get_wrapper().admin.applications.post(
            data={
                'name': name,
                'groups': groups,
                'rights': rights,
                'enabled': enabled
            }
        )

    def update_application(
        self,
        id: int,
        name: Optional[str] = None,
        enabled: bool = True,
        groups: Optional[List[int]] = None,
        rights: Optional[List[str]] = None
    ):
        """Update an API application

        PATCH /api/admin/applications/:id

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Application-updateApplication
        """
        data = {
            'id': id,
            'enabled': enabled
        }
        if groups:
            data['groups'] = groups
        if rights:
            data['rights'] = rights
        if name:
            data['name'] = name
        return self.get_wrapper().admin.applications.post(
            data=data
        )

    def run_cypher_query(
        self,
        sourcekey: str, query: str,
        with_digest: bool = False,
        with_degree: bool = False,
    ):
        """Executes a cypher query.

        POST /api/:sourceKey/graph/run/query

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Query-runQuery
        """
        return self.get_wrapper().post(
            f"{sourcekey}/graph/run/query",
            data={
                'query': query,
                'dialect': 'cypher',
                'withDigest': with_digest,
                'withDegree': with_degree
            }
        )

    def get_visualizations_tree(self, sourcekey: str):
        """Get the visualizations tree for the given sourcekey

        GET /api/:sourceKey/visualizations/tree

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Visualization-getVisualizationTree
        """
        return self.get_wrapper().get(
            f"{sourcekey}/visualizations/tree",
        )

    def get_visualization(
        self, sourcekey: str, id: int,
        with_digest: bool = False,
        with_degree: bool = False
    ):
        """Get the visualization by sourcekey and id

        GET /api/:sourceKey/visualizations/:id

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Visualization-getVisualization
        """
        return self.get_wrapper().get(
            f"{sourcekey}/visualizations/{id}",
            params={
                'withDigest': with_digest,
                'withDegree': with_degree
            }
        )

    def create_visualization(
        self,
        sourcekey: str,
        title: str,
        nodes: list,
        edges: list
    ):
        """
        Create a visualization for the source with sourcekey

        POST /api/:sourceKey/visualizations

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Visualization-createVisualization
        and https://doc.linkurio.us/server-sdk/2.10.9/publish-a-widget/ to see a  JS example
        """
        return self.get_wrapper().post(
            f"{sourcekey}/visualizations",
            data={
                'title': title,
                'layout': {'algorithm': 'force', 'mode': 'fast'},
                'nodes': nodes,
                'edges': edges,
                'alternativeIds': {
                    'node': 'id',
                    'edge': 'id'
                }
            }
        )

    def update_visualization(
        self, sourcekey: str, id: int,
        visualization: dict = None,
        force_lock: bool = False,
        do_layout: bool = False
    ):
        """
        Update the visualization identified by sourcekey and id

        PATCH /api/:sourceKey/visualizations/:id

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Visualization-updateVisualization
        """
        data = {}
        if visualization is None:
            visualization = {}
        data['visualization'] = visualization
        if force_lock:
            data['forceLock'] = True
        if do_layout:
            data['doLayout'] = True
        return self.get_wrapper().patch(
            f"{sourcekey}/visualizations/{id}",
            data=data
        )

    def delete_visualization(self, sourcekey: str, id: int):
        """
        Delete the visualization identified by sourcekey and id

        DELETE /api/:sourceKey/visualizations/:id

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Visualization-deleteVisualization
        """
        return self.get_wrapper().delete(f"{sourcekey}/visualizations/{id}")

    def get_visualization_share_rights(self, sourcekey: str, id: int):
        """Get the list of shares for the visualization identified by sourcekey and id

        GET /api/:sourceKey/visualizations/:id/shares

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Visualization-getVisualizationShares
        """
        return self.get_wrapper().get(
            f"{sourcekey}/visualizations/{id}/shares"
        )

    def share_visualization(self, sourcekey: str, id: int, user_id: int, right: str):
        """Share the visualization identified by sourcekey and id with the user identified by user_id

        PUT /api/:sourceKey/visualizations/:id/share/:userId

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Visualization-shareVisualization
        """
        return self.get_wrapper().put(
            f"{sourcekey}/visualizations/{id}/share/{user_id}",
            data={
                'right': right
            }
        )

    def unshare_visualization(self, sourcekey: str, id: int, user_id: int):
        """Remove the share of the visualization identified by sourcekey and id from the user identified by user_id

        DELETE /api/:sourceKey/visualizations/:id/share/:userId

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-Visualization-unshareVisualization
        """
        return self.get_wrapper().delete(
            f"{sourcekey}/visualizations/{id}/share/{user_id}"
        )

    def get_users(
        self,
        starts_with: Optional[str] = None,
        contains: Optional[str] = None,
        group_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort_by: Optional[str] = None,
        sort_direction: Optional[str] = None
    ):
        """Get and search all the users.

        Only the first limit (10 by defaults) are returned.
        Use the parameters to search among all the users.

        GET /api/users

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-User-searchUsers
        """
        params = {}
        if starts_with:
            params['starts_with'] = starts_with
        if contains:
            params['contains'] = contains
        if group_id:
            params['group_id'] = group_id
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if sort_by:
            params['sort_by'] = sort_by
        if sort_direction:
            params['sort_direction'] = sort_direction
        return self.get_wrapper().users.get(params=params)

    def get_groups(self, sourcekey: str):
        """Get all the groups for the sourcekey

        GET /api/admin/:sourceKey/groups

        see https://doc.linkurio.us/server-sdk/2.10.9/apidoc/#api-User-getGroups
        """
        return self.get_wrapper().admin.get(f"{sourcekey}/groups")
