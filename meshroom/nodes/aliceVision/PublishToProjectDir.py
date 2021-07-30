from __future__ import print_function

__version__ = "0.1"

from meshroom.core import desc
import shutil
import glob
import os
import json
import subprocess
import math

class PublishToProjectDir(desc.Node):
    size = desc.DynamicNodeSize('inputFiles')

    category = 'Export'
    documentation = '''
Copy Wavefront affects to the project directory.
'''

    inputs = [
        desc.ListAttribute(
            elementDesc=desc.File(
                name="input",
                label="Input",
                description="",
                value="",
                uid=[0],
            ),
            name="inputFiles",
            label="Input Files",
            description="Input Files to publish.",
            group="",
        ),
        desc.File(
            name="output",
            label="Base Output Folder",
            description="",
            value="/mnt/models",
            uid=[0],
        ),
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='''verbosity level (critical, error, warning, info, debug).''',
            value='info',
            values=['critical', 'error', 'warning', 'info', 'debug'],
            exclusive=True,
            uid=[],
            ),
        ]

    outputs = [
        desc.File(
            name='output_folder',
            label='Output Folder',
            description='Folder that was created for model.',
            value="{outputValue}/{inputFilesValue}/directory",
            uid=[],
            group=""
        ),
    ]

    def getLodPostfix(self, inputFiles):
        vector_num, texture_size = None, None

        for inputFilePattern in inputFiles:
            for inputFile in glob.glob(inputFilePattern.value):
                if os.path.splitext(inputFile)[1] == ".mtl":
                    pass

                if os.path.splitext(inputFile)[1] == ".png":
                    retobj = subprocess.run("file {}".format(inputFile),
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)
                    if retobj.returncode == 0:
                        texture_size = math.floor(int(
                            retobj.stdout.decode().split(",")[1].split(" ")[3]
                        ) / 1024)

                if os.path.splitext(inputFile)[1] == ".obj":
                    retobj = subprocess.run("grep ^v {} | wc -l".format(
                        inputFile),
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

                    if retobj.returncode == 0:
                        vector_num = math.floor(
                            int(retobj.stdout.decode().strip()) / 1024
                        )

        if vector_num and texture_size:
            return "{}k_{}k".format(texture_size, vector_num)

        return None

    def resolvedPaths(self, inputFiles, outDir, lod_postfix):
        paths = {}
        for inputFile in inputFiles:
            for f in glob.glob(inputFile.value):
                basename,extname = os.path.splitext(os.path.basename(f))

                paths[f] = os.path.join(outDir, "{}_{}{}".format(
                    basename, lod_postfix, extname
                ))

        return paths

    def getOutputDirectory(self, prjname, base_dir):
        return os.path.join(base_dir, prjname)

    def processChunk(self, chunk):
        ### Starting an in place REPL shell
        # import code
        # import readline
        # import inspect
        # code.InteractiveConsole(dict(globals(), **locals())).interact()

        try:
            if not chunk.node.output.value:
                chunk.logger.warning('No Base Output Folder')
                return

            graph = chunk.node._attributes.parent().parent().parent()
            prjname = graph.name

            output_dir = self.getOutputDirectory(prjname,
                                                 chunk.node.output.value)
            chunk.logManager.start(chunk.node.verboseLevel.value)

            chunk.logger.info('Output Directory: {}'.format(output_dir))

            lod_postfix = self.getLodPostfix(chunk.node.inputFiles.value)
            if not lod_postfix:
                chunk.logger.warning('No model files')
                return

            chunk.logger.info('LOD Postfix: {}'.format(lod_postfix))

            if not os.path.exists(output_dir):
                os.mkdir(output_dir)

            data = {
                graph.IO.Keys.Header: graph.header,
                graph.IO.Keys.Graph: graph.toDict(),
            }

            with open(os.path.join(output_dir, "src_{}.mg".format(lod_postfix)),
                      'w') as jsonFile:
                json.dump(data, jsonFile, indent=4)

            if not chunk.node.inputFiles:
                chunk.logger.warning('Nothing to publish')
                return

            outFiles = self.resolvedPaths(chunk.node.inputFiles.value,
                                          output_dir,
                                          lod_postfix)

            if not outFiles:
                error = 'Publish: input files listed, but nothing to publish'
                chunk.logger.error(error)
                chunk.logger.info('Listed input files: {}'.format([i.value for i in chunk.node.inputFiles.value]))
                raise RuntimeError(error)

            for iFile, oFile in outFiles.items():
                chunk.logger.info('Publish file {} into {}'.format(iFile, oFile))
                shutil.copyfile(iFile, oFile)

                if os.path.splitext(oFile)[1] == ".mtl":
                    cmdline = "sed -i s/.png$/_{}.png/ {}".format(
                        lod_postfix, oFile
                    )
                    retobj = subprocess.run(cmdline,
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

                    if retobj.returncode > 0:
                        chunk.logger.error('CMD: {} FAILED: {}'.format(
                            cmdline, retobj.stderr.decode()
                        ))
                        raise RuntimeError(retobj.stderr.decode())

                if os.path.splitext(oFile)[1] == ".obj":
                    cmdline = "sed -i s/.mtl$/_{}.mtl/ {}".format(
                        lod_postfix, oFile
                    )
                    retobj = subprocess.run(cmdline,
                                            shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

                    if retobj.returncode > 0:
                        chunk.logger.error('CMD: {} FAILED: {}'.format(
                            cmdline, retobj.stderr.decode()
                        ))
                        raise RuntimeError(retobj.stderr.decode())

            chunk.logger.info('Publish end')

            chunk.node.output_folder.value = output_dir
            chunk.node.output_folder.valueChanged.emit()

        finally:
            chunk.logManager.end()
