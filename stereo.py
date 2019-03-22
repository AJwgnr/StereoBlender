import bpy
from bpy import context
from math import sin, cos, radians
import random as rand
import yaml

class Stereo:
    
    def __init__(self, path):
        self.__clearScene()
        self.__readStereoConfigurationFile(path)
        self.__setupScene()
        return
    
    # Removes all objects. material and textures from the Blender scene
    def __clearScene(self):
        # Remove all materials
        for material in bpy.data.materials:
            material.user_clear();
            bpy.data.materials.remove(material);
        # Remove all textures
        for texture in bpy.data.textures:
            texture.user_clear();
            bpy.data.textures.remove(texture);

        bpy.context.scene.use_nodes = True
        tree = bpy.context.scene.node_tree
        links = tree.links
     
        # clear default nodes
        for n in tree.nodes:
            tree.nodes.remove(n)
            
        #Remove objects from previsous scenes
        for item in bpy.data.objects:
            #select all objects  
            bpy.data.objects[item.name].select_set(True)
        #delete all selected objects
        bpy.ops.object.delete()
        return

    # Setups the Blender scene by adding a light for the rendering and also setting the render scene to stereo mode 
    def __setupScene(self):
        bpy.ops.object.light_add()
        light = None
        for item in bpy.data.objects:  
            if item.type == "LIGHT": 
                light = item
        light.location = (0,0,5)
        light.data.use_shadow = False
        light.data.energy = 5.0
        light.select_set(False)
        
        # Set the resolution of the camera/scene
        self.context = bpy.context
        self.scene = self.context.scene
        self.scene.render.resolution_x = self.config["camera"]["resolution_horizontal"]
        self.scene.render.resolution_y = self.config["camera"]["resolution_vertical"]
        self.scene.render.use_multiview = True
        self.scene.render.views_format = 'STEREO_3D'
        return

    # Reads the YAML configuration file with the stereo specification 
    def __readStereoConfigurationFile(self, path):
        with open(path, 'r') as stream:
            try:
                self.config = yaml.load(stream)
                #print(self.config)
            except yaml.YAMLError as exc:
                print(exc)
        return 


    # creates two cameras as stereo system
    def createStereoSetup(self):
        # Add a camera to the scene
        bpy.ops.object.camera_add()
        # Retrieve the generated camera from the scene
        camera = bpy.data.objects[0] 
        if camera.type == "CAMERA": 
            camera.select_set(True)
            
            # Set the camera parameter loaded from the configuration file
            camera.data.stereo.convergence_distance = 10000
            camera.data.sensor_height  = self.config["camera"]["sensor_height"]
            camera.data.sensor_width= self.config["camera"]["sensor_width"]
            camera.data.lens = self.config["lens"]["focal_length"]
            camera.data.stereo.interocular_distance = self.config["stereo"]["baseline"]
            # Move camera in the scene
            camera.rotation_mode = 'XYZ'
            camera.rotation_euler = (1.5708, 0, 0)
            camera.location = (0,0,1)
            print('Stereo setup created')
            
            areas = bpy.context.screen.areas

            # Change stereoscopic parameter to visualizing both cameras and the corresponding frustums
            for area in areas:
                if (area.type == "VIEW_3D"):
                    area.spaces[0].show_stereo_3d_cameras           = self.config["visualization"]["camera"]
                    area.spaces[0].show_stereo_3d_convergence_plane = self.config["visualization"]["plane"]
                    area.spaces[0].show_stereo_3d_volume            = self.config["visualization"]["volume"]
                    area.spaces[0].stereo_3d_volume_alpha           = self.config["visualization"]["alpha"]
         
            # Turning the created camera into the active camera for this scene
            currentCameraObj = bpy.data.objects[bpy.context.active_object.name]
            self.scene.camera = currentCameraObj   
            # Printing the information about the created setu
            self.printStereoConfiguration()
        
 
        

    # prints the configuration of the created stereo system
    def printStereoConfiguration(self):
        
        # Prints camera parameters
        print(str("\n")+ "Camera settings:")
        #print('Field of View Vertical: ' + str(self.config["camera"]["focal_length"])) 
        #print('Field of View Horizontal: ' + str(self.config["camera"]["focal_length"]))
        
        print('Sensor Resolution Horizontal (px):  '+ str(self.config["camera"]["resolution_horizontal"]))
        print('Sensor Resolution Vertical (px): '+ str(self.config["camera"]["resolution_vertical"]))
        print('Pixel Size Horizontal (μm): '+ str(self.config["camera"]["pixel_size_horizontal"]))
        print('Pixel Size Vertical (μm): '+ str(self.config["camera"]["pixel_size_vertical"]))
        
        # Prints lens parameters
        print(str("\n")+ "Lens settings: ")
        print('Focal Length (mm): ' + str(self.config["lens"]["focal_length"])) 
        
        # Prints stereo parameters
        print(str("\n") + "Stereo settings: ")
        print('Baseline (m): ' + str(self.config["stereo"]["baseline"])) 
        print('Intersection FOV/Minimum Depth (m): '+ str()) 
        print('Estimated Depth Error: ' + str()) 
        return

    def calculateFov():
        return


    # Creates an artificial stereo dataset with corresponding ground truth data
    def createStereoDataset(self):
        if(self.config["dataset"]["generation"] == True):
            for count in range(0,self.config["dataset"]["size"]):
                self.__clearScene()
                self.__setupScene
                self.createStereoSetup()
                # Adds objects randomly in the cameras field of viw
                self.__addObjectsToScene()
                #setup the depthmap calculation using blender's mist function:
                self.context.window.view_layer.use_pass_mist = True
                #self.context.window.view_layer.mist_settings.falloff = 'LINEAR'
                #self.context.window.view_layer.intensity = 0.0
                #self.context.window.view_layer.depth = dist
                #print(dist)

                self.scene.use_nodes = True
                tree = self.scene.node_tree
                links = tree.links
                
                
                self.scene.render.use_multiview = True
                self.scene.render.views_format = 'STEREO_3D'
                rl = tree.nodes.new(type="CompositorNodeRLayers")
                composite = tree.nodes.new(type = "CompositorNodeComposite")
                composite.location = 200,0
                
                
                # ouput the depthmap:
                links.new(rl.outputs['Mist'],composite.inputs['Image'])
                self.scene.render.use_multiview = False

                self.scene.render.filepath = self.config["dataset"]["path"] + 'DepthMap/' + 'DepthMap_' +str(count)+'.png'
                bpy.ops.render.render( write_still=True ) 
                # output the stereoscopic images:
                links.new(rl.outputs['Image'],composite.inputs['Image'])
                self.scene.render.use_multiview = True
                self.scene.render.filepath = self.config["dataset"]["path"]+ 'StereoImage/' + 'Stereoscopic_' +str(count)+'.png'
                bpy.ops.render.render( write_still=True ) 
        return



    # Adds a set of objects randomly to the scene
    def __addObjectsToScene(self):
        self.magn = 5
        self.__createCube('Cube','Material')
        self.__createCube('Cube.001','Material.001')
        self.__createCone('Cone','Material.002')
        self.__createTorus('Torus','Material.003')
        self.__createSphere('Sphere','Material.004')
        return

    # Creates a Cube with a CubeName and a material
    def __createCube(self, CubeName, MatName):
        bpy.ops.mesh.primitive_cube_add(location=((0.3-rand.random())*self.magn, (10+rand.random())*self.magn, (0.3+rand.random())*self.magn))
    # Creates a Cone with a CubeName and a material
    def __createCone(self,ConeName, MatName):
        bpy.ops.mesh.primitive_cone_add(location=((0.5-rand.random())*self.magn, (10+rand.random())*self.magn, (0.6+rand.random())*self.magn))
    # Creates a Torus with a CubeName and a material
    def __createTorus(self, TorusName, MatName):
        bpy.ops.mesh.primitive_torus_add(location=((0.35-rand.random())*self.magn, (10+rand.random())*self.magn, (0.45+rand.random())*self.magn))
    # Creates a Sphere with a CubeName and a material
    def __createSphere(self,SphereName, MatName):
        bpy.ops.mesh.primitive_uv_sphere_add(location=((0.5-rand.random())*self.magn, (10+rand.random())*self.magn, (0.5+rand.random())*self.magn))


# Provide full path to the configuration file
stereo = Stereo("/home/lenovo/Desktop/StereoBlender/stereo.yaml")
stereo.createStereoSetup()
stereo.createStereoDataset()


