/********************************************************************************
 * Copyright (c) 2009, 2010 MontaVista Software, Inc and Others.
 * This program and the accompanying materials are made available under the terms
 * of the Eclipse Public License v1.0 which accompanies this distribution, and is
 * available at http://www.eclipse.org/legal/epl-v10.html
 *
 * Contributors:
 * Anna Dushistova (MontaVista) - initial API and implementation
 * Lianhao Lu (Intel)			- Modified to add other file operations.
 ********************************************************************************/
package org.yocto.bc.remote.utils;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;

import javax.swing.JOptionPane;

import org.eclipse.core.runtime.CoreException;
import org.eclipse.core.runtime.FileLocator;
import org.eclipse.core.runtime.IProgressMonitor;
import org.eclipse.core.runtime.IStatus;
import org.eclipse.core.runtime.MultiStatus;
import org.eclipse.core.runtime.OperationCanceledException;
import org.eclipse.core.runtime.Path;
import org.eclipse.core.runtime.Status;
import org.eclipse.core.runtime.SubProgressMonitor;
import org.eclipse.osgi.util.NLS;
import org.eclipse.ptp.remote.core.IRemoteConnection;
import org.eclipse.ptp.remote.core.IRemoteProcess;
import org.eclipse.ptp.remote.core.IRemoteProcessBuilder;
import org.eclipse.ptp.remote.core.IRemoteServices;
import org.eclipse.ptp.remote.core.exception.RemoteConnectionException;
import org.eclipse.rse.core.IRSECoreStatusCodes;
import org.eclipse.rse.core.RSECorePlugin;
import org.eclipse.rse.core.model.IHost;
import org.eclipse.rse.core.model.ISubSystemConfigurationCategories;
import org.eclipse.rse.core.model.ISystemRegistry;
import org.eclipse.rse.core.subsystems.ISubSystem;
import org.eclipse.rse.services.IService;
import org.eclipse.rse.services.clientserver.messages.SystemMessageException;
import org.eclipse.rse.services.files.IFileService;
import org.eclipse.rse.services.files.IHostFile;
import org.eclipse.rse.services.shells.HostShellProcessAdapter;
import org.eclipse.rse.services.shells.IHostShell;
import org.eclipse.rse.services.shells.IShellService;
import org.eclipse.rse.subsystems.files.core.servicesubsystem.IFileServiceSubSystem;
import org.eclipse.rse.subsystems.shells.core.subsystems.servicesubsystem.IShellServiceSubSystem;
import org.eclipse.rse.subsystems.terminals.core.ITerminalServiceSubSystem;
import org.yocto.bc.ui.Activator;
import org.yocto.bc.ui.wizards.install.Messages;

public class RemoteHelper {
	
	public static final String FTP_PROXY = "ftp_proxy";
	public static final String HTTP_PROXY = "http_proxy";
	public static final String HTTPS_PROXY = "https_proxy";
	public static final String SOCKS_PROXY = "socks_proxy";
	public static final String GIT_PROXY_COMMAND = "GIT_PROXY_COMMAND";
	
	public static IHost getRemoteConnectionByName(String remoteConnection) {
		if (remoteConnection == null)
			return null;
		IHost[] connections = RSECorePlugin.getTheSystemRegistry().getHosts();
		for (int i = 0; i < connections.length; i++)
			if (connections[i].getAliasName().equals(remoteConnection))
				return connections[i];
		return null; // TODO Connection is not found in the list--need to react
		// somehow, throw the exception?

	}
	
	public static IHost getRemoteConnectionByURI(URI uri) {
		if (uri == null)
			return null;
		
		Map<String, IHost> connectionsForHost = new HashMap<String, IHost>();
		IHost[] connections = RSECorePlugin.getTheSystemRegistry().getHosts();

		IHost firstConnection = null;
		for (int i = 0; i < connections.length; i++) {
			if (connections[i].getHostName().equals(uri.getHost())) {
				if (firstConnection == null)
					firstConnection = connections[i];
				connectionsForHost.put(connections[i].getAliasName(), connections[i]);
			}
		}
		
		if (connectionsForHost.size() == 1)
			return firstConnection;
		
		String[] choices = new String[connectionsForHost.size()];
		connectionsForHost.keySet().toArray(choices);

		String picked = (String)JOptionPane.showInputDialog(null, "Choose a connection for the current project:"
	                , "Connection chooser", JOptionPane.QUESTION_MESSAGE
	                , null, choices, choices[0]);
		
		return connectionsForHost.get(picked); 
	}
	
	public static String getRemoteHostName(String remoteConnection)
	{
		final IHost host = getRemoteConnectionByName(remoteConnection);
		if(host == null)
			return null;
		else
			return host.getHostName();
	}

	public static IFileService getConnectedRemoteFileService(IHost currentConnection, IProgressMonitor monitor) throws Exception {
		final ISubSystem subsystem = getFileSubsystem(currentConnection);

		if (subsystem == null)
			throw new Exception(Messages.ErrorNoSubsystem);

		try {
			subsystem.connect(monitor, false);
		} catch (CoreException e) {
			throw e;
		} catch (OperationCanceledException e) {
			throw new CoreException(Status.CANCEL_STATUS);
		}

		if (!subsystem.isConnected())
			throw new Exception(Messages.ErrorConnectSubsystem);

		return ((IFileServiceSubSystem) subsystem).getFileService();
	}
	
	public static IHostFile[] getRemoteDirContent(IHost currentConnection, String remoteParent, String fileFilter, int fileType, IProgressMonitor monitor){
		
		try {
			IFileService fileServ = getConnectedRemoteFileService(currentConnection, monitor);
			return fileServ.list(remoteParent, fileFilter, fileType, monitor);
		} catch (SystemMessageException e) {
			e.printStackTrace();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}

	public static IService getConnectedRemoteFileService(IRemoteConnection currentConnection, IProgressMonitor monitor) throws Exception {
		final ISubSystem subsystem = getFileSubsystem(getRemoteConnectionByName(currentConnection.getName()));

		if (subsystem == null)
			throw new Exception(Messages.ErrorNoSubsystem);

		try {
			subsystem.connect(monitor, false);
		} catch (CoreException e) {
			throw e;
		} catch (OperationCanceledException e) {
			throw new CoreException(Status.CANCEL_STATUS);
		}

		if (!subsystem.isConnected())
			throw new Exception(Messages.ErrorConnectSubsystem);

		return ((IFileServiceSubSystem) subsystem).getFileService();
	}
	
	public static ISubSystem getFileSubsystem(IHost host) {
		if (host == null)
			return null;
		ISubSystem[] subSystems = host.getSubSystems();
		for (int i = 0; i < subSystems.length; i++) {
			if (subSystems[i] instanceof IFileServiceSubSystem)
				return subSystems[i];
		}
		return null;
	}
	
	public static IService getConnectedShellService(
			IHost currentConnection, IProgressMonitor monitor) throws Exception {
		final ISubSystem subsystem = getShellSubsystem(currentConnection);

		if (subsystem == null)
			throw new Exception(Messages.ErrorNoSubsystem);

		try {
			subsystem.connect(monitor, false);
		} catch (CoreException e) {
			throw e;
		} catch (OperationCanceledException e) {
			throw new CoreException(Status.CANCEL_STATUS);
		}

		if (!subsystem.isConnected())
			throw new Exception(Messages.ErrorConnectSubsystem);

		return ((IShellServiceSubSystem) subsystem).getShellService();
	}
	
	public static ISubSystem getShellSubsystem(IHost host) {
		if (host == null)
			return null;
		ISubSystem[] subSystems = host.getSubSystems();
		for (int i = 0; i < subSystems.length; i++) {
			if (subSystems[i] instanceof IShellServiceSubSystem)
				return subSystems[i];
		}
		return null;
	}

	public static IHost[] getSuitableConnections() {
		
		//we only get RSE connections with files&cmds subsystem
		ArrayList <IHost> filConnections = new ArrayList <IHost>(Arrays.asList(RSECorePlugin.getTheSystemRegistry()
				.getHostsBySubSystemConfigurationCategory(ISubSystemConfigurationCategories.SUBSYSTEM_CATEGORY_FILES))); //$NON-NLS-1$
		
		ArrayList <IHost> terminalConnections = new ArrayList <IHost>(Arrays.asList(RSECorePlugin.getTheSystemRegistry()
				.getHostsBySubSystemConfigurationCategory("terminal")));//$NON-NLS-1$
		
		ArrayList<Object> shellConnections = new ArrayList<Object>(Arrays.asList(RSECorePlugin.getTheSystemRegistry()
				.getHostsBySubSystemConfigurationCategory("shells"))); //$NON-NLS-1$

		Iterator <IHost>iter = filConnections.iterator();
		while(iter.hasNext()){
			IHost fileConnection = iter.next();
			if(!terminalConnections.contains(fileConnection) && !shellConnections.contains(fileConnection)){
				iter.remove();
			}
		}
		
		return (IHost[]) filConnections.toArray(new IHost[filConnections.size()]);
	}
	
	public static void deleteRemoteFile(IHost connection, String remoteExePath,
			IProgressMonitor monitor) throws Exception {
		
		assert(connection!=null);
		monitor.beginTask(Messages.InfoUpload, 100);
		
		IFileService fileService;
		try {
			fileService = (IFileService) getConnectedRemoteFileService(
							connection,
							new SubProgressMonitor(monitor, 5));
	
			Path remotePath = new Path(remoteExePath);
			if(fileService.getFile(remotePath.removeLastSegments(1).toString(), 
					remotePath.lastSegment(), 
					new SubProgressMonitor(monitor, 5)).exists()) {
				fileService.delete(remotePath.removeLastSegments(1).toString(), 
						remotePath.lastSegment(), 
						new SubProgressMonitor(monitor, 10));
			}
		} finally {
			monitor.done();
		}
		return;
	}
	
	public static void putRemoteFile(IHost connection, String localExePath, String remoteExePath,
			IProgressMonitor monitor) throws Exception {
		
		assert(connection!=null);
		monitor.beginTask(Messages.InfoUpload, 100);
		
		IFileService fileService;
		try {
			fileService = (IFileService) getConnectedRemoteFileService(
							connection,
							new SubProgressMonitor(monitor, 5));
			File file = new File(localExePath);
			Path remotePath = new Path(remoteExePath);
			IHostFile remoteFile = fileService.getFile(remotePath.removeLastSegments(1).toString(), 
					remotePath.lastSegment(), 
					new SubProgressMonitor(monitor, 5));
			if(remoteFile.exists() && !remoteFile.isDirectory()) {
				fileService.delete(remotePath.removeLastSegments(1).toString(), 
						remotePath.lastSegment(), 
						new SubProgressMonitor(monitor, 10));
			}
			fileService.upload(file, remotePath.removeLastSegments(1)
					.toString(), remotePath.lastSegment(), true, null, null,
					new SubProgressMonitor(monitor, 80));
		} finally {
			monitor.done();
		}
		return;
	}
	
	public static void putRemoteFileInPlugin(IHost connection, String locaPathInPlugin, String remoteExePath,
			IProgressMonitor monitor) throws Exception {
		
		assert(connection!=null);
		monitor.beginTask(Messages.InfoUpload, 100);
		
		IFileService fileService;
		try {
			fileService = (IFileService) getConnectedRemoteFileService(
							connection,
							new SubProgressMonitor(monitor, 5));
			InputStream  inputStream = FileLocator.openStream(
				    Activator.getDefault().getBundle(), new Path(locaPathInPlugin), false);
			Path remotePath = new Path(remoteExePath);
			/*
			if(!fileService.getFile(remotePath.removeLastSegments(1).toString(), 
					remotePath.lastSegment(), 
					new SubProgressMonitor(monitor, 5)).exists()) {
			}
			*/
			/*
			fileService.upload(inputStream, remotePath.removeLastSegments(1)
					.toString(), remotePath.lastSegment(), true, null,
					new SubProgressMonitor(monitor, 80));
					*/
			//TODO workaround for now
			//in case the underlying scp file service doesn't support inputStream upload
			BufferedInputStream bis = new BufferedInputStream(inputStream);
			File tempFile = File.createTempFile("scp", "temp"); //$NON-NLS-1$ //$NON-NLS-2$
			FileOutputStream os = new FileOutputStream(tempFile);
			BufferedOutputStream bos = new BufferedOutputStream(os);
			byte[] buffer = new byte[1024];
			int readCount;
			while( (readCount = bis.read(buffer)) > 0)
			{
				bos.write(buffer, 0, readCount);
			}
			bos.close();
			fileService.upload(tempFile, remotePath.removeLastSegments(1)
					.toString(), remotePath.lastSegment(), true, null, null,
					new SubProgressMonitor(monitor, 80));
			// Need to change the permissions to match the original file
			// permissions because of a bug in upload
			remoteShellExec(
					connection,
					"", "chmod", "+x " + spaceEscapify(remotePath.toString()), new SubProgressMonitor(monitor, 5)); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
			
		} finally {
			monitor.done();
		}
		return;
	}
	
	public static void getRemoteFile(IHost connection, String localExePath, String remoteExePath,
			IProgressMonitor monitor) throws Exception {
		
		assert(connection!=null);
		monitor.beginTask(Messages.InfoDownload, 100);
		
		IFileService fileService;
		try {
			fileService = (IFileService) getConnectedRemoteFileService(
							connection,
							new SubProgressMonitor(monitor, 10));
			File file = new File(localExePath);
			file.deleteOnExit();
			monitor.worked(5);
			Path remotePath = new Path(remoteExePath);
			fileService.download(remotePath.removeLastSegments(1).toString(), 
					remotePath.lastSegment(),file,true, null,
					new SubProgressMonitor(monitor, 85));
			// Need to change the permissions to match the original file
			// permissions because of a bug in upload
			//RemoteApplication p = remoteShellExec(
			//		config,
			//		"", "chmod", "+x " + spaceEscapify(remotePath.toString()), new SubProgressMonitor(monitor, 5)); //$NON-NLS-1$ //$NON-NLS-2$ //$NON-NLS-3$
			//Thread.sleep(500);
			//p.destroy();
			
		} finally {
			monitor.done();
		}
		return;
	}
	
	public static IHostFile getRemoteHostFile(IHost host, String remoteFilePath, IProgressMonitor monitor){
		assert(host != null);
		monitor.beginTask(Messages.InfoDownload, 100);
		
		try {
			IFileService fileService = (IFileService) getConnectedRemoteFileService(host, new SubProgressMonitor(monitor, 10));
			Path remotePath = new Path(remoteFilePath);
			IHostFile remoteFile = fileService.getFile(remotePath.removeLastSegments(1).toString(), remotePath.lastSegment(), new SubProgressMonitor(monitor, 5));
			return remoteFile;
		} catch (Exception e) {
	    }finally {
			monitor.done();
		}
		return null;
	}
	
	public static ITerminalServiceSubSystem getTerminalSubSystem(
            IHost connection) {
        ISystemRegistry systemRegistry = RSECorePlugin.getTheSystemRegistry();
        ISubSystem[] subsystems = systemRegistry.getSubSystems(connection);
        for (int i = 0; i < subsystems.length; i++) {
        	if (subsystems[i] instanceof ITerminalServiceSubSystem) {
                ITerminalServiceSubSystem subSystem = (ITerminalServiceSubSystem) subsystems[i];
                return subSystem;
            }
        }
        return null;
    }
	
	public static String spaceEscapify(String inputString) {
		if (inputString == null)
			return null;

		return inputString.replaceAll(" ", "\\\\ "); //$NON-NLS-1$ //$NON-NLS-2$
	}
	
	private final static String EXIT_CMD = "exit"; //$NON-NLS-1$
	private final static String CMD_DELIMITER = ";"; //$NON-NLS-1$
	
	public static Process remoteShellExec(IHost connection,
			String prelaunchCmd, String remoteCommandPath, String arguments,
			IProgressMonitor monitor) throws CoreException {
		
		monitor.beginTask(NLS.bind(Messages.RemoteShellExec_1,
				remoteCommandPath, arguments), 10);
		String realRemoteCommand = arguments == null ? spaceEscapify(remoteCommandPath)
				: spaceEscapify(remoteCommandPath) + " " + arguments; //$NON-NLS-1$

		String remoteCommand = realRemoteCommand + CMD_DELIMITER + EXIT_CMD;

		if(prelaunchCmd != null) {
			if (!prelaunchCmd.trim().equals("")) //$NON-NLS-1$
				remoteCommand = prelaunchCmd + CMD_DELIMITER + remoteCommand;
		}

		IShellService shellService;
		Process p = null;
		try {
			shellService = (IShellService) getConnectedShellService(
							connection,
							new SubProgressMonitor(monitor, 7));

			// This is necessary because runCommand does not actually run the
			// command right now.
			String env[] = new String[0];
			try {
				IHostShell hostShell = shellService.launchShell(
						"", env, new SubProgressMonitor(monitor, 3)); //$NON-NLS-1$
				hostShell.writeToShell(remoteCommand);
				p = new HostShellProcessAdapter(hostShell);
			} catch (Exception e) {
				if (p != null) {
					p.destroy();
				}
				abort(Messages.RemoteShellExec_2, e,
						IRSECoreStatusCodes.EXCEPTION_OCCURRED);
			}
		} catch (Exception e1) {
			abort(e1.getMessage(), e1,
					IRSECoreStatusCodes.EXCEPTION_OCCURRED);
		}

		monitor.done();
		return p;
	}
	
	public static String[] getEnvProxyVars(String gitProxyScriptPath, 
			String ftpProxyURL, int ftpProxyPort, 
			String httpProxyURL, int httpProxyPort, 
			String httpsProxyURL, int httpsProxyPort,
			String socksProxyURL, int socksProxyPort){
		String gitProxy = GIT_PROXY_COMMAND + "=" + gitProxyScriptPath;
		String ftpProxy = FTP_PROXY + "=" + ftpProxyURL + ":" + ftpProxyPort;
		String httpProxy = HTTP_PROXY + "=" + httpProxyURL + ":" + httpProxyPort;
		String httpsProxy = HTTPS_PROXY + "=" + httpsProxyURL + ":" + httpsProxyPort;
		String socksProxy = SOCKS_PROXY + "=" + socksProxyURL + ":" + socksProxyPort;
		return new String[]{gitProxy, ftpProxy, httpProxy, httpsProxy, socksProxy};
	}
	
	public static Process runCommandRemote(IHost connection, String initialDir,
			String cmd, String arguments,
			IProgressMonitor monitor) throws CoreException {
		
		monitor.beginTask(NLS.bind(Messages.RemoteShellExec_1,
				cmd, arguments), 10);

		String remoteCommand = cmd + " " + arguments +  CMD_DELIMITER + EXIT_CMD;

		IShellService shellService;
		Process p = null;
		try {
			shellService = (IShellService) getConnectedShellService(connection, new SubProgressMonitor(monitor, 7));

			// FIXME: maybe create this file directly remote - and set the variable to a default location only if running under proxy
			// FIXME detect proxy url  from system or modify interface to insert proxies for remote 
			String intelProxyURL = "http://proxy-us.intel.com";
			String env[] = getEnvProxyVars("/home/root/socks-gw", intelProxyURL, 911, intelProxyURL, 911, intelProxyURL, 911, intelProxyURL, 1080);
			try {
				IHostShell hostShell = shellService.runCommand(initialDir, remoteCommand, env, new SubProgressMonitor(monitor, 3));
				p = new HostShellProcessAdapter(hostShell);
			} catch (Exception e) {
				if (p != null) {
					p.destroy();
				}
//				abort(Messages.RemoteShellExec_2, e, IRSECoreStatusCodes.EXCEPTION_OCCURRED);
			}
		} catch (Exception e1) {
//			abort(e1.getMessage(), e1, IRSECoreStatusCodes.EXCEPTION_OCCURRED);
			e1.printStackTrace();
		}
 		return p;
	}
	
	public static ProcessStreamBuffer handleRunCommandRemote(IHost connection, String initialDir,
			String cmd, String arguments,
			IProgressMonitor monitor, CommandResponseHandler cmdHandler){
	
		ProcessStreamBuffer buffer = new ProcessStreamBuffer();
		try {
			Process process = runCommandRemote(connection, initialDir, cmd, arguments, monitor);
			
			if (process == null)
				throw new Exception("An error has occured while trying to run remote command!");
			BufferedReader inbr = new BufferedReader(new InputStreamReader(process.getInputStream()));
			BufferedReader errbr = new BufferedReader(new InputStreamReader(process.getErrorStream()));
			String info;
			boolean cancel = false;
			while (!cancel) {
				if(monitor.isCanceled()) {
					cancel = true;
					throw new InterruptedException("User Cancelled");
				}
				info = null;
				//reading stderr
				while (errbr.ready()) {
					info = errbr.readLine();
					buffer.addErrorLine(info);
					//some application using stderr to print out information
					cmdHandler.response(info, false);
				}
				//reading stdout
				while (inbr.ready()) {
					info = inbr.readLine();
					buffer.addOutputLine(info);
					cmdHandler.response(info, false);
				}
				if (info == null)
					cancel = true;
			}
			
		} catch (Exception e) {
			e.printStackTrace();
		}
		return buffer;
	}
	
	public static IRemoteProcess createProcessRemote(IRemoteConnection connection, IRemoteServices remoteServices, 
			IProgressMonitor monitor, 
			String[] cmdArray, String[] envp){
		if (!connection.isOpen()) {
			try {
				connection.open(monitor);
			} catch (RemoteConnectionException e1) {
				e1.printStackTrace();
			}
		}

		if (!remoteServices.isInitialized()) {
			remoteServices.initialize();
		}

		IRemoteProcessBuilder processBuilder = remoteServices.getProcessBuilder(connection, cmdArray);

		Map<String, String> remoteEnvMap = processBuilder.environment();

		for (String envVar : envp) {
			String[] splitStr = envVar.split("="); //$NON-NLS-1$
			if (splitStr.length > 1) {
				remoteEnvMap.put(splitStr[0], splitStr[1]);
			} else if (splitStr.length == 1) {
				remoteEnvMap.put(splitStr[0], ""); //$NON-NLS-1$
			}
		}

		// combine stdout and stderr
		processBuilder.redirectErrorStream(true);
		
		IRemoteProcess process = null;
		try {
			process = processBuilder.start();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return process;
	}
	
	/**
	 * Throws a core exception with an error status object built from the given
	 * message, lower level exception, and error code.
	 * 
	 * @param message
	 *            the status message
	 * @param exception
	 *            lower level exception associated with the error, or
	 *            <code>null</code> if none
	 * @param code
	 *            error code
	 */
	public static void abort(String message, Throwable exception, int code) throws CoreException {
		IStatus status;
		if (exception != null) {
			MultiStatus multiStatus = new MultiStatus(Activator.PLUGIN_ID, code, message, exception);
			multiStatus.add(new Status(IStatus.ERROR, Activator.PLUGIN_ID, code, exception.getLocalizedMessage(), exception));
			status= multiStatus;
		} else {
			status= new Status(IStatus.ERROR, Activator.PLUGIN_ID, code, message, null);
		}
		throw new CoreException(status);
	}

	public static URI createNewURI(URI oldURI, String name) {
		try {
			String sep = oldURI.getPath().endsWith("/") ? "" : "/";
			return new URI(oldURI.getScheme(), oldURI.getHost(), oldURI.getPath() + sep + name, oldURI.getFragment());
		} catch (URISyntaxException e) {
			e.printStackTrace();
			return null;
		}
	}

	public static boolean fileExistsRemote(IHost conn, IProgressMonitor monitor, String path) {
		try {
			IFileService fs = getConnectedRemoteFileService(conn, monitor);
			int nameStart = path.lastIndexOf("/");
			String parentPath = path.substring(0, nameStart);
			String name = path.substring(nameStart + 1);
			IHostFile hostFile = fs.getFile(parentPath, name, monitor);
			return hostFile.exists();
		} catch (Exception e) {
			e.printStackTrace();
		}
		return false;
	}
	
}
