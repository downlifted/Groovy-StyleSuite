const { exec } = require('child_process');
const path = require('path');

module.exports = {
  runGroovyStyleSuite: function (input, callback) {
    // Construct the command to run the Python script
    const pythonScript = path.join(__dirname, 'app.py');  // Ensure 'app.py' is in the same directory
    const command = `python ${pythonScript}`;

    console.log('Executing command:', command);

    // Execute the Python script
    exec(command, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${error.message}`);
        callback(`Error: ${error.message}`);
        return;
      }

      if (stderr) {
        console.error(`Error output: ${stderr}`);
        callback(`Error output: ${stderr}`);
        return;
      }

      console.log(`Script output: ${stdout}`);
      callback(stdout);  // Return the output to whatever called this function
    });
  }
};
