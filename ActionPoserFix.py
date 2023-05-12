import bpy
import math

active = bpy.context.active_object.name

data = bpy.data
armature = data.armatures[(active)]
ap_poses = armature.ap_poses

obj = bpy.data.objects[(active)]

context = bpy.context
scene = context.scene

id = -1

#loop over all poses
for pose in ap_poses:
    id += 1
    bid = -1
    globdrv = pose.driver_add('influence').driver
    
    #loop over all target bones
    for bone in ap_poses[(id)].bones:
        bid += 1
        posename = ap_poses[(id)].name
        targetname = (bone.bone)
        drivertarget = ap_poses[(id)].target
        driverbone = ap_poses[(id)].bone
        transformchannel = ap_poses[(id)].channel
        transformspace = ap_poses[(id)].space
        mixmethod = ap_poses[(id)].mix
        min = ap_poses[(id)].transform_min
        max = ap_poses[(id)].transform_max
        action = ap_poses[(id)].action
        start = ap_poses[(id)].start_frame
        end = ap_poses[(id)].end_frame
        influence = ap_poses[(id)].bones[bid].influence
        
        #convert channels back with an if statement cause i suck at life lol
        channel = transformchannel
        if channel == "LOC_X":
            channel = "LOCATION_X"
        elif channel == "LOC_Y":
            channel = "LOCATION_Y"
        elif channel == "LOC_Z":
            channel = "LOCATION_Z"
        elif channel == "ROT_X":
            channel = "ROTATION_X"
        elif channel == "ROT_Y":
            channel = "ROTATION_Y"
        elif channel == "ROT_Z":
            channel = "ROTATION_Z"
        
        #convert spaces back with an if statement cause i still suck at life
        space = transformspace
        if space == "LOCAL_SPACE":
            space = "LOCAL"
        elif space == "WORLD_SPACE":
            space = "WORLD"
        
        #select bone
        bpy.context.object.data.bones.active = obj.pose.bones[(targetname)].bone
        
        #add constraints
        cnstrn = context.active_pose_bone.constraints.new('ACTION')
        cnstrn.name = "AP-" + posename
        cnstrn.target = drivertarget
        cnstrn.subtarget = driverbone
        cnstrn.transform_channel = channel
        cnstrn.target_space = space
        cnstrn.mix_mode = mixmethod
        cnstrn.influence = influence
        cnstrn.min = min
        cnstrn.max = max
        cnstrn.action = action
        cnstrn.frame_start = start
        cnstrn.frame_end = end
        
        #create combo drivers
        if ap_poses[(id)].type == "COMBO":
            pose_a = ap_poses[(id)].corr_pose_A
            pose_b = ap_poses[(id)].corr_pose_B
            
            channel_a = ap_poses[(pose_a)].channel
            channel_b = ap_poses[(pose_b)].channel
            
            min_a = ap_poses[(pose_a)].transform_min
            max_a = ap_poses[(pose_a)].transform_max
            min_b = ap_poses[(pose_b)].transform_min
            max_b = ap_poses[(pose_b)].transform_max
            
            iscombo_a = 0
            iscombo_b = 0
            if ap_poses[(pose_a)].type == 'COMBO':
                iscombo_a = 1
            if ap_poses[(pose_b)].type == 'COMBO':
                iscombo_b = 1 
            
            cnstrn.use_eval_time = True

            drv = obj.driver_add('pose.bones["'+str(targetname)+'"].constraints["AP-'+str(posename)+'"].eval_time').driver
            
            drv.type = 'SCRIPTED'
            
            #more conversions with if statements lets goooo
            isrot_a = 0
            isrot_b = 0
            
            if channel_a == "LOC_X":
                lrs_a = 'location'
                driverchannel_a = 0
            elif channel_a == "LOC_Y":
                lrs_a = 'location'
                driverchannel_a = 1
            elif channel_a == "LOC_Z":
                lrs_a = 'location'
                driverchannel_a = 2
            elif channel_a == "ROT_X":
                lrs_a = 'rotation_euler'
                driverchannel_a = 0
                isrot_a += 1
            elif channel_a == "ROT_Y":
                lrs_a = 'rotation_euler'
                driverchannel_a = 1
                isrot_a += 1
            elif channel_a == "ROT_Z":
                lrs_a = 'rotation_euler'
                driverchannel_a = 2
                isrot_a += 1
                
            if channel_b == "LOC_X":
                lrs_b = 'location'
                driverchannel_b = 0
            elif channel_b == "LOC_Y":
                lrs_b = 'location'
                driverchannel_b = 1
            elif channel_b == "LOC_Z":
                lrs_b = 'location'
                driverchannel_b = 2
            elif channel_b == "ROT_X":
                lrs_b = 'rotation_euler'
                driverchannel_b = 0
                isrot_b += 1
            elif channel_b == "ROT_Y":
                lrs_b = 'rotation_euler'
                driverchannel_b = 1
                isrot_b += 1
            elif channel_b == "ROT_Z":
                lrs_b = 'rotation_euler'
                driverchannel_b = 2
                isrot_b += 1
                
            #Pose A
            var_a = drv.variables.new()
            var_a.name = "var_a"
            if iscombo_a == 0:
                var_a.targets[0].id_type = 'OBJECT'
                var_a.targets[0].id = obj
                drivertarget_a = ap_poses[(pose_a)].bone
                var_a.targets[0].data_path = 'pose.bones["'+str(drivertarget_a)+'"].'+str(lrs_a)+'['+str(driverchannel_a)+']'
            elif iscombo_a != 0:
                var_a.targets[0].id_type = 'OBJECT'
                var_a.targets[0].id = obj
                var_a_bone = ap_poses[(pose_a)].bones[0].bone
                var_a.targets[0].data_path = 'pose.bones["'+str(var_a_bone)+'"].constraints["AP-'+str(pose_a)+'"].eval_time'
        
                
            #Pose B
            var_b = drv.variables.new()
            var_b.name = "var_b"
            if iscombo_b == 0:
                var_b.targets[0].id_type = 'OBJECT'
                var_b.targets[0].id = obj
                drivertarget_b = ap_poses[(pose_b)].bone
                print (drivertarget_b)
                var_b.targets[0].data_path = 'pose.bones["'+str(drivertarget_b)+'"].'+str(lrs_b)+'['+str(driverchannel_b)+']'
            elif iscombo_b != 0:
                var_b.targets[0].id_type = 'OBJECT'
                var_b.targets[0].id = obj
                var_b_bone = ap_poses[(pose_b)].bones[0].bone
                var_b.targets[0].data_path = 'pose.bones["'+str(var_b_bone)+'"].constraints["AP-'+str(pose_b)+'"].eval_time'
            
            if isrot_a != 0:
                min_a = math.radians(min_a)
                max_a = math.radians(max_a)
            if isrot_b != 0:
                min_b = math.radians(min_b)
                max_b = math.radians(max_b)
            
            if iscombo_a + iscombo_b == 0:
                drv.expression = 'min(((var_a - '+str(min_a)+') / ('+str(max_a)+' - '+str(min_a)+')), ((var_b - '+str(min_b)+') / ('+str(max_b)+' - '+str(min_b)+')))'
            elif iscombo_a != 0 and iscombo_b == 0:
                drv.expression = 'min(var_a, ((var_b - '+str(min_b)+') / ('+str(max_b)+' - '+str(min_b)+')))'
            elif iscombo_a == 0 and iscombo_b != 0:
                drv.expression = 'min(var_a, ((var_b - '+str(min_b)+') / ('+str(max_b)+' - '+str(min_b)+')))'
            elif iscombo_a != 0 and iscombo_b != 0:
                drv.expression = 'min(var_a, var_b)'