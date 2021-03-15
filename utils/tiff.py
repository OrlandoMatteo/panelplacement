import glob
import rasterio
import numpy as np

def createPercentileTiff(perc_threshold=85):
    #Obtain the list of files for the typical days
    beamList=sorted(glob.glob("/media/HD/blockRaster/beam_*[!.aux.xml,!.dbf,!.py,!.csv,!.qpj]"))
    diffList=sorted(glob.glob("/media/HD/blockRaster/diff_*[!.aux.xml,!.dbf,!.py,!.csv,!.qpj]"))

    # Shape of a typical day tiff
    s=rasterio.open(beamList[0]).read(1).shape
    # number of files for the typical days
    l=len(beamList)

    # matrix to store the sum of the files
    matrix=np.zeros((s[0],s[1],l))
    # matrix to store the final Tiff
    percentileMatrix=np.zeros((s[0],s[1]))

    for x in range(len(beamList)) :
        matrix[:,:,x]=rasterio.open(beamList[x]).read(1)+rasterio.open(diffList[x]).read(1)
        print(x*100/l,end='\r')

    # Calculate percentile and store it in the matrix
    total=s[0]
    c=0
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[1]):
            percentileMatrix[i,j]=np.percentile(matrix[i,j,:],perc_threshold,axis=0)
        c+=1
    print(c*100/total,end='\r')

    # template for metadata extraction
    template=rasterio.open(beamList[0])

    # Saving the mamtrix to a file
    out_meta = template.meta.copy()
    out_meta.update(
        dtype=np.float64)
    with rasterio.open("data/percentile"+str(perc_threshold)+".tiff", "w",**out_meta) as dest:
        dest.write(percentileMatrix,1)
