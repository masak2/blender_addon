require './_define.rb'
require 'find'
require 'fileutils'

require $cmn_program + '/ruby/file_copy.rb'


dstDir = "C:/Users/LMisa/AppData/Roaming/Blender Foundation/Blender/4.0/scripts/addons/masak"



for filepath in  Dir::entries(".")

	if File::ftype(filepath) != "file"
		next
	end
	if !filepath.end_with?(".py")
		next
	end
	dstPath = dstDir + "/" + filepath
	#p dstPath
	filecopy( filepath, dstPath)

end



p "success"