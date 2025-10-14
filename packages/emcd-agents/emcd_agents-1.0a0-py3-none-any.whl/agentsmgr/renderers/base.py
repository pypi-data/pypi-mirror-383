# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Coder renderer base class and type definitions.

    Defines base class for coder-specific renderers which handle
    path resolution, targeting mode validation, and output structure
    for different AI coding assistants.
'''


from . import __


TargetMode: __.typx.TypeAlias = __.typx.Literal[
    'default', 'per-user', 'per-project', 'nowhere' ]
ExplicitTargetMode: __.typx.TypeAlias = __.typx.Literal[
    'per-user', 'per-project' ]


class RendererBase( __.immut.Object ):
    ''' Base class for coder-specific rendering and path resolution.

        Provides interface that all coder renderers must implement for
        coder-specific behavior including targeting mode validation and
        path resolution for output files.
    '''

    name: str
    modes_available: frozenset[ ExplicitTargetMode ]
    mode_default: ExplicitTargetMode
    memory_filename: str

    def validate_mode( self, mode: ExplicitTargetMode ) -> None:
        ''' Validates targeting mode is supported by this coder.

            Raises TargetModeNoSupport if mode not supported.
        '''
        if mode not in self.modes_available:
            raise __.TargetModeNoSupport( self.name, mode )

    def resolve_base_directory(
        self,
        mode: ExplicitTargetMode,
        target: __.Path,
        configuration: __.cabc.Mapping[ str, __.typx.Any ],
        environment: __.cabc.Mapping[ str, str ],
    ) -> __.Path:
        ''' Resolves base output directory for this coder.

            Determines appropriate output location based on targeting mode,
            respecting precedence of environment variables over file
            configuration over coder defaults. For per-user mode, checks
            environment first, then configuration file overrides, then
            falls back to coder-specific defaults. For per-project mode,
            constructs path within project structure.
        '''
        raise NotImplementedError

    def produce_output_structure( self, item_type: str ) -> str:
        ''' Produces subdirectory structure for item type.

            Translates generic item type to coder-specific directory
            structure. Most coders use same structure, but some may
            have different conventions.
        '''
        return item_type


RENDERERS: __.accret.Dictionary[ str, RendererBase ] = (
    __.accret.Dictionary( ) )
