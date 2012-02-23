package org.yocto.sdk.remotetools.actions;

import java.io.File;
import java.io.FilenameFilter;

import org.eclipse.jface.dialogs.Dialog;
import org.eclipse.jface.dialogs.IDialogConstants;
import org.eclipse.jface.dialogs.IDialogSettings;
import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Combo;
import org.eclipse.swt.widgets.Composite;
import org.eclipse.swt.widgets.Control;
import org.eclipse.swt.widgets.Label;
import org.eclipse.swt.widgets.Shell;
import org.eclipse.swt.widgets.Text;
import org.yocto.sdk.remotetools.Activator;
import org.yocto.sdk.remotetools.Messages;
import org.yocto.sdk.remotetools.SWTFactory;

public class BsptoolSettingDialog extends Dialog {
	
	public BsptoolSettingDialog(Shell parent) {
		super(parent);
		// TODO Auto-generated constructor stub
	}

	static protected String title="BspTool";;
	protected boolean showPid=false;
	protected Float time;
	protected Button showPidButton;
	protected Button outLocButton;
	protected Text timeText;
	
	public boolean getShowPid() {
		return showPid;
	}
	
	public Float getTime() {
		return time;
	}
	
	protected void configureShell(Shell newShell) {
		super.configureShell(newShell);
		newShell.setText(title);
	}
	
	protected Control createDialogArea(Composite parent) {
		Composite comp=(Composite)super.createDialogArea(parent);
		GridLayout topLayout = new GridLayout();
		comp.setLayout(topLayout);
		
		/*argument*/
		SWTFactory.createVerticalSpacer(comp, 1);
		createInternal(comp);
		
		return comp;
	}
	
	protected void createInternal(Composite parent)
	{
		Composite projComp = new Composite(parent, SWT.NONE);
		GridLayout projLayout = new GridLayout();
		projLayout.numColumns = 4;
		projLayout.marginHeight = 0;
		projLayout.marginWidth = 0;
		projComp.setLayout(projLayout);
		GridData gd = new GridData(GridData.FILL_HORIZONTAL);
		projComp.setLayoutData(gd);
		
		Label label = new Label(projComp, SWT.NONE);
		label.setText (Messages.BspTool_name);
		gd = new GridData();
		gd.horizontalSpan = 2;
		label.setLayoutData(gd);
		
		Text text = new Text(projComp, SWT.NONE);
		text.setText(""); 
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 2;
		text.setLayoutData(gd);
		
		Label label1 = new Label(projComp, SWT.NONE);
		label1.setText (Messages.BspTool_karch);
		gd = new GridData();
		gd.horizontalSpan = 2;
		label1.setLayoutData(gd);
		
		// gather available kernel arcitectures from file path
		//       scripts/lib/bsp/substrate/target/arch
		// exclude "common"
		
		File dir = new File("./poky-contrib/scripts/lib/bsp/substrate/target/arch");

		String[] children = dir.list();
		if (children == null) {
		    // Either dir does not exist or is not a directory
		} else {
		    for (int i=0; i<children.length; i++) {
		        // Get filename of file or directory
		        String filename = children[i];
		    }
		}

		// Do not return any files that start with 'common'.
		FilenameFilter filter = new FilenameFilter() {
		    public boolean accept(File dir, String name) {
		        return !name.startsWith("common");
		    }
		};
		children = dir.list(filter);
	
		Combo combo = new Combo (projComp, SWT.NONE);
		combo.setItems (children);
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 2;
		combo.setLayoutData(gd);
		
		Label label11 = new Label(projComp, SWT.NONE);
		label11.setText (Messages.BspTool_out_dir);
		gd = new GridData();
		gd.horizontalSpan = 1;
		label11.setLayoutData(gd);
		
		Text text1 = new Text(projComp, SWT.NONE);
		text1.setText(""); 
		gd = new GridData(GridData.FILL_HORIZONTAL);
		gd.horizontalSpan = 2;
		text1.setLayoutData(gd);
		
		outLocButton = SWTFactory.createPushButton(projComp,
				Messages.BspTool_out_dir_btn, null);
		outLocButton.addSelectionListener(new SelectionAdapter() {

			public void widgetSelected(SelectionEvent evt) {
				handleOutLocButton();
				//updateLaunchConfigurationDialog();
				updateOutLocText();
			}
		});
		gd = new GridData();
		gd.horizontalSpan = 1;
		outLocButton.setLayoutData(gd);
			
		
	}

	protected void updateOutLocText() {
		// TODO Auto-generated method stub
		
	}

	protected void handleOutLocButton() {
		// TODO something
	}
}
