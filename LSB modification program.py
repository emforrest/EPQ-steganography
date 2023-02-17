#Eleanor Forrest EPQ - How can I conceal a message within a bitmap image, and then retrieve it?

#Python Solution - LSB modification program

#IMPORTANT - To run the program, you will need the Python Imaging Library installed on your device. To do this:
    #1) Open the Command Prompt (in the search bar next to the Start icon,
        #type 'cmd' and click Command Prompt)
    #2) Type 'python -m pip install pip'. You may need to upgrade it - type
        #'python -m pip install --upgrade pip'
    #3) When done, type 'python -m pip install pillow'


#Start

#Subroutines

def decimalToBinary(x): 
    unit = 65536 #produces a 16-bit number
    binary = ''
    while unit >=1:
        if x - unit >=0:
            binary += '1'
            x -= unit #means x = x - unit
        else:
            binary += '0'
        #endif
        unit = int(unit / 2)
    #endwhile

    #reduce to 8 bits if required.
    if binary[:8] == '00000000':
        binary = binary[9:]
    #endif
    
    return binary
#endsub

def binaryToDecimal(x):
    bits = len(x)
    unit = 2**(bits-1) #for 8 bits, this is 128, the exact number needed to end up with 1 at the final bit.
    decimal = 0

    for char in x:
        if char == '1':
            decimal += unit
        #endif
        unit = int(unit / 2)
    #endfor

    return int(decimal)
#endsub

def randomPixelOrder(key, pixelsNeeded, totalPixels):

    random.seed(key) #so every time the same key is used, the same sequence is created.
    
    #create an array of random pixels 
    pixelOrder = []
    for i in range(0, pixelsNeeded):
        randomPixel = random.randint(0, totalPixels)
        while randomPixel in pixelOrder == True:
            randomPixel = random.randint(1, totalPixels) #try another number until it finds one that isn't already there.
        else:
            pixelOrder.append(randomPixel)
        #endwhile
    #endfor


    return pixelOrder
#endsub

def getRGB(pixel, imageWidth, image):

    #get the x and y coordinates of the pixel
    pixelx = pixel % imageWidth
    pixely = pixel // imageWidth

    #access the pixel's red green and blue channels 
    pixelRGB = image[pixelx, pixely]
    pixelRed = pixelRGB[0]
    pixelGreen = pixelRGB[1]
    pixelBlue = pixelRGB[2]

    return pixelx, pixely, pixelRed, pixelGreen, pixelBlue

def initialiseEmbed(): #resets all values
    #1. import the message 
    found = False
    while not found:
        messageFileName = input('Enter the name of the file containing the secret message (including .txt):')
        try:
            messageFile = open(messageFileName, 'r') #opens the file in read mode
            message = messageFile.read() #this contains the actual message.
            messageFile.close()
            found = True
            print('File found.')
        except FileNotFoundError: 
            print('The specified file was not found. Make sure it is located in the same folder as this program, then re-run it.')
            input('Press Enter to close the program.')
            sys.exit()
        except UnicodeDecodeError:
            print('The specified file appears to be the wrong file format. Make sure you are using a .txt file and try again.')
            input('Press Enter to close the program.')
            sys.exit()
        #endtry
    #endwhile

    if len(message) > 65536: #the largest message stored by 16 bits (this is very large)
        print('The message provided is too large. Please summarise your points and try again.')
        input('Press Enter to close the program.')
        sys.exit()
    #endif

    #2. import the cover image
    
    imageFileName = input('Enter the name of the file containing the cover image (including the file format eg .jpg):')
    try:
        imageFile = Image.open(imageFileName) #uses the Image module to access the image
        imageFile.close()
            
        #copy the image to a new file
        newFileName = 'stegoimage.bmp' #other formats compress the data which messes up the binary

        if os.path.exists(newFileName):
            print('The file "{0}" already exists. Please delete it or move it to another folder and try again.'.format(newFileName))
            input('Press Enter to close the program.')
            sys.exit()
        else:
            f = open(newFileName, 'x') #creates a new file
            f.close()
            os.system('copy {0} {1}'.format(imageFileName, newFileName))
            imageFile = Image.open(newFileName) #we want to modify the new image, not the old one.
        #endif
                
        imageWidth = imageFile.width
        imageHeight = imageFile.height
            
        print('File found.')
        found = True
    except FileNotFoundError:
        print('The specified file was not found. Make sure it is located in the same folder as this program, then re-run it.')
        input('Press Enter to close the program.')
        sys.exit()
    except: #PIL.UnidentifiedImageError
        print('The specified image appears to be unreadable. Check the file format is suitable and try again.')
        input('Press Enter to close the program.')
        sys.exit()
    #endtry


    messageLength = len(message)
    pixelsNeeded = math.ceil((messageLength *8 +16) /3)# *8 because each character converts to 8 bits, adds 16 for the length of the message, divides by 3 as there are 3 colour channels, and is rounded up by math.ceil().
    totalPixels = imageWidth * imageHeight

    if pixelsNeeded > totalPixels:
        print('The image provided is not large enough to contain your message. Please select a larger image or shorten your message and try again.')
        input('Press Enter to close the program.')
        sys.exit()
    #endif

    #3. input the key and use it to generate a random pixel order.

    key = input('Enter the key. This can be a word or number, but must be shared with the recipient:')
    pixelOrder = randomPixelOrder(key, pixelsNeeded, totalPixels)
    
    return message, imageFile, imageWidth, imageHeight, newFileName, pixelOrder
#endsub
    

def embed(message, imageFile, imageWidth, imageHeight, newFileName, pixelOrder):

    #1. Convert the message into ASCII
    
    messageASCII = ''
    #add the length of the message in binary first
    messageLength = decimalToBinary(len(message))
    messageLength = messageLength[1:]
    if len(messageLength) <16:
        x=16-len(messageLength)
        messageLength = '0'*x + messageLength #messageLength should always be 16-bit
    messageASCII+=messageLength
    
    for char in message:
        char = ord(char) #gives the ASCII code but in decimal, I need to convert it to binary.
        char = decimalToBinary(char)
        messageASCII+=char
    #endfor

    #2 adjust the colour values of each randomly selected pixel in turn.

    image = imageFile.load()
    multiple = 0
    for i in range(0, len(pixelOrder)):
        pixel = pixelOrder[i]
        pixelx, pixely, pixelRed, pixelGreen, pixelBlue = getRGB(pixel, imageWidth, image)

        #select the bits from the message to be added
        value1 = 3*multiple
        value2 = 3*multiple +1
        value3 = 3*multiple +2
        
        if value1 < len(messageASCII):
            r = messageASCII[value1]
        else:
            r = -1
        #endif
        if value2 < len(messageASCII):
            g = messageASCII[value2]
        else:
            g = -1
        #endif
        if value3 < len(messageASCII):
            b = messageASCII[value3]
        else:
            b = -1
        #endif

        #slice the pixel colour values to remove the current LSB, then attach the new LSB.
        if r != -1: 
            pixelRed = decimalToBinary(pixelRed)
            newRed = pixelRed[:7] + r
            newRed = binaryToDecimal(newRed)
            image[pixelx, pixely] = (newRed, pixelGreen, pixelBlue, 255)
            pixelRed = newRed
        else:
            image[pixelx, pixely] = (pixelRed, pixelGreen, pixelBlue, 255)
        #endif
        if g != -1:
            pixelGreen = decimalToBinary(pixelGreen)
            newGreen = pixelGreen[:7] + g
            newGreen = binaryToDecimal(newGreen)
            image[pixelx, pixely] = (pixelRed, newGreen, pixelBlue, 255)
            pixelGreen = newGreen
        else:
            image[pixelx, pixely] = (pixelRed, pixelGreen, pixelBlue, 255)
        #endif
        if b != -1:
            pixelBlue = decimalToBinary(pixelBlue)
            newBlue = pixelBlue[:7] + b
            newBlue = binaryToDecimal(newBlue)
            image[pixelx, pixely] = (pixelRed, pixelGreen, newBlue, 255)
            pixelBlue = newBlue
        else:
            image[pixelx, pixely] = (pixelRed, pixelGreen, pixelBlue, 255)
        #endif
        
        multiple +=1
    #endfor
    imageFile.save(newFileName)
    imageFile.close()
    print('The new image has been saved as {0}.'.format(newFileName))
    
#endsub

def initialiseExtract():

    #1 input the stegoimage
    stegoimageName = input('Enter the name of the file containing the stegoimage (including the file format eg .jpg):')
    try:
        stegoimageFile = Image.open(stegoimageName) #attempts to open the file
        imageWidth = stegoimageFile.width
        imageHeight = stegoimageFile.height
        print('File found')
    except FileNotFoundError:
        print('The specified file was not found. Make sure it is located in the same folder as this program, then re-run it.')
        input('Press Enter to close the program.')
        sys.exit()
    except: #PIL.UnidentifiedImageError
        print('The specified image appears to be unreadable. Check the file format is suitable and try again.')
        input('Press Enter to close the program.')
        sys.exit()
    #endtry

    #2 generate an empty file for the message to be stored in
    if os.path.exists('secret_message.txt'):
        print('The file \'secret_message.txt\' already exists. Please delete it or move it to another folder and try again.')
        input('Press Enter to close the program.')
        sys.exit()
    else:
        messageFile = open('secret_message.txt', 'x') #creates a new file
    #endif

    #3 use the key to generate the random pixel order as before. Here it only takes 6 pixels as these are the pixels with the length of the message. Once these have been extracted the key can be used again to generate the same list up until the final pixel used.
    key = input('Enter the key the sender gave you:')
    pixelOrder = randomPixelOrder(key, 6, imageWidth*imageHeight)

    return messageFile, stegoimageFile, imageWidth, imageHeight, pixelOrder, key
#endsub

def extract(messageFile, stegoimageFile, imageWidth, imageHeight, pixelOrder, key):

    #1 start with just the length of the message
    length = ''
    stegoimage = stegoimageFile.load()
    for i in range(0, len(pixelOrder)):
        pixel = pixelOrder[i]
        pixelx, pixely, pixelRed, pixelGreen, pixelBlue = getRGB(pixel, imageWidth, stegoimage) #Note: pixelx and pixely aren't actually used again this time

        pixelRed = decimalToBinary(pixelRed)
        redLSB = pixelRed[7:]
        length += redLSB #adds the LSB of the red channel to a new variable length, which holds the length of the file in binary
        pixelGreen = decimalToBinary(pixelGreen)
        greenLSB = pixelGreen[7:]
        length += greenLSB
        pixelBlue = decimalToBinary(pixelBlue)
        blueLSB = pixelBlue[7:]
        length += blueLSB
    #endfor

    #length is now an 18-bit binary number
    length = length[:16] #remove the last two bits as these aren't part of the length.
    length = binaryToDecimal(length)

    #2 recreate the random pixel order using this length

    length = math.ceil((length *8 +16) /3)
    pixelOrder = randomPixelOrder(key, length, imageWidth*imageHeight)
            
    #3 extract the message using similar code to in #1
    
    messageASCII = ''
    for i in range(0, length):
        pixel = pixelOrder[i]
        pixelx, pixely, pixelRed, pixelGreen, pixelBlue = getRGB(pixel, imageWidth, stegoimage)
        pixelRed = decimalToBinary(pixelRed)
        redLSB = pixelRed[7:]
        messageASCII += redLSB 
        pixelGreen = decimalToBinary(pixelGreen)
        greenLSB = pixelGreen[7:]
        messageASCII += greenLSB
        pixelBlue = decimalToBinary(pixelBlue)
        blueLSB = pixelBlue[7:]
        messageASCII += blueLSB
        
    #endfor

    messageASCII = messageASCII[16:] #removes the length from the start

    #4 convert the message back into normal characters
    start = 0
    end = 8
    while end <= len(messageASCII):
        character = messageASCII[start:end] #slice messageASCII into 8 bit slices which correlate to a character
        character = character[1:] #there must not be a leading zero
        character = binaryToDecimal(character)
        character = chr(character) #the chr function converts a denary ASCII code into a character
        messageFile.write(character)
        start += 8
        end += 8
    #endwhile

    print('The message has been saved as \'secret_message.txt\'.')

    messageFile.close()
    stegoimageFile.close()
    
#endsub


def menu():
    mode = 0
    while mode !=3: #while the user hasn't selected Quit
        print('What would you like to do? \n\t1. Embed a message \n\t2. Extract a message\n\t3. Quit\nEnter 1, 2 or 3')
        validMode = False
        while not validMode:
            try:
                mode = int(input('>>>'))
                if 0<mode<=3:
                    validMode = True
                else:
                    print('Please only enter 1-3')
                #endif
            except ValueError:
                print('Please enter a number')
            #endtry
        #endwhile

        #call the specified function
        if mode == 1:
            message, imageFile, imageWidth, imageHeight, newFileName, pixelOrder = initialiseEmbed()
            embed(message, imageFile, imageWidth, imageHeight, newFileName, pixelOrder)
        elif mode == 2:
            messageFile, stegoimageFile, imageWidth, imageHeight, pixelOrder, key = initialiseExtract()
            extract(messageFile, stegoimageFile, imageWidth, imageHeight, pixelOrder, key)
        else:
            print('Thank you for using this software.')
        #endif
    #endwhile
#endsub


def main():
    print('Welcome. This software allows you to embed a message in an image and then retrieve it. First, a few technical things. \n\t1) The message must be stored in a plain text file.\n\t2) The image used must use the RGB/RGBA colour format such as .jpg or .png. However, transparent .png files will appear changed.\n\t3)The new image is saved as \'stegoimage.bmp\' and the retrieved message as \'secret_message.txt\'. If you already have files with these names you will need to move or rename them.\n\t4) You will notice some small errors in the extracted message. I\'d recommend writing the message multiple times so the recipient can properly understand, or reduce the frequency of errors by using a large image.\n\n')
    menu()
#endsub

#Imports
    
from PIL import Image #for image handling
import os #for file handling, especially creating new files
import random #for generating a random sequence
import sys #used to exit the program so the user can move their files
import math #for calculations

#Begin the program

if __name__ == '__main__':
    main()
#endif
