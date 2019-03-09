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
test
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
        light = bpy.data.objects['Point']
        light.data.use_shadow = False
        light.data.energy = 5.0
        light.select_set(False)
        
        self.scene = bpy.context.scene
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
                print(self.config)
            except yaml.YAMLError as exc:
                print(exc)
        return 


    # creates two cameras as stereo system
    def createStereoSetup(self):
        # Add a camera to the scene
        bpy.ops.object.camera_add()
        # Retrieve the generated camera from the scene
        camera = bpy.data.objects[0]
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
        self.printStereoConfiguration()
        

    # prints the configuration of the created stereo system
    def printStereoConfiguration(self):
        print(str("\n")+ "Camera settings:")
        #print('Field of View Vertical: ' + str(self.config["camera"]["focal_length"])) 
        #print('Field of View Horizontal: ' + str(self.config["camera"]["focal_length"]))
        
        print('Sensor Resolution Horizontal: '+ str(self.config["camera"]["resolution_horizontal"]))
        print('Sensor Resolution Vertical: '+ str(self.config["camera"]["resolution_vertical"]))
        print('Pixel Size Horizontal: '+ str(self.config["camera"]["pixel_size_horizontal"]))
        print('Pixel Size Vertical: '+ str(self.config["camera"]["pixel_size_vertical"]))
        
        print(str("\n")+ "Lens settings: ")
        print('Focal Length: ' + str(self.config["lens"]["focal_length"])) 
        
        print(str("\n") + "Stereo settings: ")
        print('Baseline: ' + str(self.config["stereo"]["baseline"])) 
        print('Intersection FOV (Minimum Depth): '+ str()) 
        print('Estimated Depth Error: ' + str()) 
        return

    def calculateFov():
        return


    # Creates an artificial stereo dataset with corresponding ground truth data
    def createStereoDataset(self,scenes):
        for ii in range(0,scenes):
            
            self.__clearScene()
            self.createStereoSetup()
            # Adds objects randomly in the cameras field of viw
            self.__addObjectsToScene()
            #setup the depthmap calculation using blender's mist function:
            self.scene.render.layers['RenderLayer'].use_pass_mist = True
            self.scene.world.mist_settings.falloff = 'LINEAR'
            self.scene.world.mist_settings.intensity = 0.0
            self.scene.world.mist_settings.depth = dist
            print(dist)
            
            # ouput the depthmap:
            links.new(rl.outputs['Mist'],composite.inputs['Image'])
            self.scene.render.use_multiview = False

            self.scene.render.filepath = 'Depth_map/DepthMap_'+str(ii)+'.png'
            bpy.ops.render.render( write_still=True ) 
            # output the stereoscopic images:
            links.new(rl.outputs['Image'],composite.inputs['Image'])
            self.scene.render.use_multiview = True
            self.scene.render.filepath = 'StereoImages/Stereoscopic_'+str(ii)+'.png'
            bpy.ops.render.render( write_still=True ) 
        return



    # Adds a set of objects randomly to the scene
    def __addObjectsToScene(self):
        self.__createCube('Cube','Material')
        self.__createCube('Cube.001','Material.001')
        self.__createCone('Cone','Material.002')
        self.__createTorus('Torus','Material.003')
        self.__createSphere('Sphere','Material.004')
        return

    # Creates a Cube with a CubeName and a material
    def __createCube(self, CubeName, MatName):
        bpy.ops.mesh.primitive_cube_add(location=((0.3-rand.random())*magn, (0.3-rand.random())*magn, (0.3-rand.random())*magn))
    # Creates a Cone with a CubeName and a material
    def __createCone(self,ConeName, MatName):
        bpy.ops.mesh.primitive_cone_add(location=((0.5-rand.random())*magn, (0.4-rand.random())*magn, (0.6-rand.random())*magn))
    # Creates a Torus with a CubeName and a material
    def __createTorus(self, TorusName, MatName):
        bpy.ops.mesh.primitive_torus_add(location=((0.35-rand.random())*magn, (0.55-rand.random())*magn, (0.45-rand.random())*magn))
    # Creates a Sphere with a CubeName and a material
    def __createSphere(self,SphereName, MatName):
        bpy.ops.mesh.primitive_uv_sphere_add(location=((0.5-rand.random())*magn, (0.5-rand.random())*magn, (0.5-rand.random())*magn))


# Provide full path to the configuration file
stereo = Stereo("/home/lenovo/Desktop/StereoBlender/stereo.yaml")
stereo.createStereoSetup()
#stereo.createStereoDataset(10)
