import ShorelineFromImage as adpthr_py
from timeit import default_timer as timer
from osgeo import gdal
import numpy as np
# parameters for testing


#read input data
#get the spatial reference from gdal
def read_tiff_image(file_path):
    # Open the TIFF file
    dataset = gdal.Open(file_path, gdal.GA_ReadOnly)

    if dataset is None:
        print("Failed to open the TIFF file.")
        return None

    # Read the image data
    image = dataset.ReadAsArray()
    geo_transform = dataset.GetGeoTransform()
    projection = dataset.GetProjection()

    # Close the dataset
    dataset = None

    return image,geo_transform,projection




#write output

def write_tiff(output_path, data, geo_transform, projection):
    # Get the dimensions of the data
    height, width = data.shape

    # Create a new GeoTIFF file
    driver = gdal.GetDriverByName("GTiff")
    output_dataset = driver.Create(output_path, width, height, 1, gdal.GDT_Byte)

    # Set the geotransform and projection
    output_dataset.SetGeoTransform(geo_transform)
    output_dataset.SetProjection(projection)

    # Write the data to the band
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(data)

    # Close the dataset
    output_dataset = None
    
    
def in_out(func):
    """
    A decorator to read and write image data
    prepare np array for calling the c++ library
    take the output and write to a new file
    parameters: input, output, band=0
    
    """
    def wrapper(*args, **kwargs):
        #find parameters of input, output, and band
        match len(args):
            case 1:#only input
                input = args[0]
                if 'output' in kwargs:
                    output = kwargs['output']
                else:
                    raise ValueError("output file is not specified")
                if 'band' in kwargs:
                    band = kwargs['band']
                else:
                    band = 0
            case 2:#input and output
                input = args[0]
                output = args[1]
                if 'band' in kwargs:
                    band = kwargs['band']
                else:
                    band = 0
            case 3:#input, output, and band
                input = args[0]
                output = args[1]
                band = args[2]
            case 0:
                #get them from the kwargs
                if 'input' in kwargs:
                    input = kwargs['input']
                else:
                    raise ValueError("input file is not specified")
                if 'output' in kwargs:
                    output = kwargs['output']
                else:
                    raise ValueError("output file is not specified")
                if 'band' in kwargs:
                    band = kwargs['band']
                else:
                    band = 0
                    
        #read image data
        image,geo_transform,projection = read_tiff_image(input)
        #convert image to uint8
        mask = ~np.isnan(image) & (image != -9999)
        filtered = image[mask]
        minValue = np.min(filtered)
        maxValue = np.max(filtered)
        print(f"Strech the image from {minValue},{maxValue} to 0, 255")
        image[~mask] = minValue
        image_uint8 = (255 * ((image - minValue) / (maxValue- minValue))).astype(np.uint8)
        
        
        shape = image.shape
        #check if the image is multiple bands
        if len(shape) == 3:
            shape = shape[1:]
            image_uint8 = image_uint8[band,:,:]
        
        dtpye = np.int16
        output_img = np.empty(shape,dtpye)

        #processing data
        start = timer()
        print("image shape: ", image.shape)        
        params ={}        
        for key in kwargs:
            #exclude input, output, and band
           
            if not key in ['input','output','band']:
                params[key] = kwargs[key]
        #print the function name
        print("Processing data using ",func.__name__)
        print("Parameters: ",params)
        func(image_uint8,output_img,**params)    
        end = timer()
        print("Time lapse: ",end - start, " seconds.") # Time in seconds, e.g. 5.38091952400282
        

        print("Writing to ouptput")
        write_tiff(output, output_img, geo_transform, projection)
        dataset = gdal.Open(output,gdal.GA_Update)
        dataset.SetGeoTransform(geo_transform)
        dataset.SetProjection(projection)
        print("output is written to ", output)
    return wrapper


@in_out
def localthreshold(input,output,percent=100, region_size = 100, debug = False, smooth_his = True):
    # Specify the path to your TIFF image


    adpthr_py.AdaptiveThreshold(input,output,percent, region_size, debug, smooth_his)
    
@in_out
def morphological(input,output,operation = "", radius = 1, object = 0, back = 255):
    # Specify the path to your TIFF image
    
    adpthr_py.MorOp(input,output,operation=operation, radius=radius)
    
    #count the number of objects
    #read the image output
    
    num_objects = np.sum(output == object)
    print("Number of objects: ", num_objects)
    #count the number of background
    num_background = np.sum(output == back)
    print("Number of background: ", num_background)
    #count the number of pixels
    num_pixels = np.prod(output.shape)
    print("Number of pixels: ", num_pixels)
    #count the number of pixels that are not object or background
    num_other = num_pixels - num_objects - num_background
    print("Number of other pixels: ", num_other)
def Morph(input_image,output_image, command):
    # Read the input image
    image, geo_transform, projection = read_tiff_image(input_image)
    #create an empty out_img for the output
    out_img = np.zeros_like(image)
    # Apply the morphological operation
    adpthr_py.MorOp(image, out_img,operation= command)
    #change the shape to 3d

    # Write the output image
    write_tiff(output_image, out_img, geo_transform, projection)
    
def contour():
    tiff_path =  r"F:\workspace\images\regionBound.tif"
    image,geo_transform,projection = read_tiff_image(tiff_path)
    #convert image to uint8
    image = image.astype(np.uint8)
    #use a small portion of the image for testing
    image = image[4000:5000,4000:5000]


    # print the image data type
    print("Image data type: ", image.dtype)    
    shape = image.shape

    output = np.empty(shape, np.uint8)
    print("output data type: ", output.dtype)    

    #processing data
    start = timer()

    polygons = adpthr_py.Contour(image,255,0)
    end = timer()
    print("Time lapse: ",end - start, " seconds.") # Time in seconds, e.g. 5.38091952400282
    print("Number of polygons: ", len(polygons))
    print("Writing to ouptput")
    writePolygon(r"F:\workspace\images\regionBound.shp", polygons, geo_transform, projection)
    

def writePolygon(output_path, polygons, geo_transform, projection):
    """
    Write the polygons to a shapefile
    use geo_transform and project to set the spatial reference
    """
    import geopandas as gpd
    import shapely.geometry as sg
    import fiona
    import os
    import numpy as np
    import pandas as pd
    # Create a GeoDataFrame
    gdf = gpd.GeoDataFrame()
    gdf['geometry'] = None
    gdf['id'] = None
    for i in range(len(polygons)):
        if len(polygons[i]) < 4:
            continue
        gdf.loc[i,'geometry'] = sg.Polygon(polygons[i])
        gdf.loc[i,'id'] = i
    # Set the GeoDataFrame's coordinate system
    gdf.crs = projection
    # Write the GeoDataFrame to a shapefile
    gdf.to_file(output_path, driver='ESRI Shapefile')
    
    pass
        
def regionGeometry(tiff_path =  r"F:\workspace\images\segmented.tif",output = r"F:\workspace\images\regionGeometry.json"):
    # Read the TIFF image using GDAL
    image,geo_transform,projection = read_tiff_image(tiff_path)
    #convert image to uint8
    image = image.astype(np.uint8)
    outinfo = adpthr_py.objectGeometry(image)
    #save to json file
    import json
    with open(output, 'w') as f:
        json.dump(outinfo, f, indent=4)
    
    
def regionBound():
    # Specify the path to your TIFF image
    tiff_path =  r"F:\workspace\images\segmented.tif"
    output_img = r"F:\workspace\images\regionbound.tif"

    # Read the TIFF image using GDAL
    image,geo_transform,projection = read_tiff_image(tiff_path)
    #convert image to uint8
    image = image.astype(np.uint8)
    

    # print the image data type
    print("Image data type: ", image.dtype)    
    shape = image.shape
        
    output = np.empty(shape, np.uint8)
    print("output data type: ", output.dtype)    

    #processing data
    start = timer()

    adpthr_py.regionBound(image,output,obj=255,back=0)
    end = timer()
    print("Time lapse: ",end - start, " seconds.") # Time in seconds, e.g. 5.38091952400282    
    print("Writing to ouptput")
    write_tiff(output_img, output, geo_transform, projection)
    dataset = gdal.Open(output_img,gdal.GA_Update)
    dataset.SetGeoTransform(geo_transform)
    dataset.SetProjection(projection)
def db2power(image):
    return 10**(image/10)
def power2db(image):
    return 10*np.log10(image)

def lee_filter():
    pass
    import ShorelineFromImage as OOIA
    import numpy as np
    # read a sar image
    from osgeo import gdal
    import matplotlib.pyplot as plt
    #use gdal to read the image
    ds = gdal.Open(r"D:\workspace\gee_sentinel\lakes\images\lake_209_20180211_NoLee.tif")
    #read the image as a numpy array
    sar_image = ds.ReadAsArray()
    sar_image = db2power(sar_image)
    
    #create a new image to store the filtered image
    filtered_image = np.zeros(sar_image.shape)
    print(sar_image.shape)
    # for each band of the image, apply the filter
    for i in range(sar_image.shape[0]):
        print(sar_image[i].shape)
        OOIA.KuanFilter(sar_image[i],filtered_image[i],3,1)
    #convert the filtered image to db
    filtered_image = power2db(filtered_image)

    #write the filtered image to a new file
    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(r"D:\workspace\gee_sentinel\lakes\images\lake_209_20180211_kuan.tif", 
                              ds.RasterXSize, ds.RasterYSize, filtered_image.shape[0], gdal.GDT_Float32)
    outRaster.SetGeoTransform(ds.GetGeoTransform())
    outRaster.SetProjection(ds.GetProjection())
    for i in range(filtered_image.shape[0]):
        outband = outRaster.GetRasterBand(i+1)
        outband.WriteArray(filtered_image[i])
    outband.FlushCache()
    outRaster = None
    ds = None
    pass

    
def main():
    import os
    print("version of the c++ library:", adpthr_py.__version__)
    workspace = r"D:\workspace\gee_sentinel\lakes\images"
     # Segmentation
    input = "lake_209_20180211_kuan.tif"
    segmented = "segmented.tif"
    input = os.path.join(workspace,input)
    
    segmented = os.path.join(workspace,segmented)
    localthreshold(input=input,output=segmented,band = 0,percent=100, region_size = 100, debug = False, smooth_his = True)
    
    # # Morhpology
    # morh_img = 'morphology.tif'
    # morh_img = os.path.join(workspace,morh_img)
    # Morph(segmented,morh_img, 'de')
    # #contour()
    # #regionBound()
    # regionGeometry()
    pass

if __name__ == "__main__":
    main()